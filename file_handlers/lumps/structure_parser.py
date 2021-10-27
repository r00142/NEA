from enum import Enum
import codecs
import struct
import tempfile

class StructError(Exception):
    '''Error within a structure definition
    '''
    pass

#misc functions for parsing
class parse_functions():
    ### misc methods
    @staticmethod
    def ltob(bytearr): #little to big
        '''returns the input as big endian, where the input is little endian'''
        output = b""
        for x in range(2, len(bytearr)+2, 2): #steps in two along the string, reversing the blocks
            output += (bytearr[-x:][:2]) #-x to -x + 2, e.g. in "abcd" where x = 2, it gets cd
        return output

    ## from x to bytes
    @staticmethod
    def btoi(bytearr, dtype="little", signed=False):
        r'''Pass in a bytearr, datatype as big or little, and signed as True or False
        '''
        if dtype in ("big", "little") and signed in (True, False):
            return int.from_bytes(bytearr, dtype, signed=signed)
        else: raise ValueError("Datatype must be little or big, and signed must be True or False")
    @staticmethod
    def btof(bytearr, dtype="little"):
        r'''Pass in a bytearr, datatype as big or little
        '''
        if dtype in ("big", "little"):
            if dtype == "little":
                return struct.unpack("!f", parse_functions.ltob(bytearr))[0]
            else: return struct.unpack("!f", bytearr)[0]
        else: raise ValueError("Datatype must be little or big")
    @staticmethod
    def btot(bytearr, dtype="little"):
        r'''Pass in a bytearr, datatype as big or little
        '''
        if dtype in ("big", "little"):
            if dtype == "little":
                return parse_functions.ltob(bytearr).decode()
            else: return bytearr.decode()
        else: raise ValueError("Datatype must be little or big")

    ### from bytes to x
    @staticmethod
    def itob(data, dtype="little", signed=False, length=4):
        r'''Pass in data, datatype as big or little, signed as True or False, length in bytes
        '''
        if dtype in ("big", "little") and signed in (True, False):
            return int.to_bytes(data, length, dtype, signed=signed)
        else: raise ValueError("Datatype must be little or big, and signed must be True or False")
        
    @staticmethod
    def ftob(data, dtype="little"):
        r'''Pass in data, datatype as big or little
        '''
        if dtype in ("big", "little"):
            if dtype == "little":
                return struct.pack("!f", parse_functions.ltob(data))[0]
            else: return struct.pack("!f", data)[0]
        else: raise ValueError("Datatype must be little or big")
    @staticmethod
    def ttob(data, dtype="little"):
        r'''Pass in data, datatype as big or little
        '''
        if dtype in ("big", "little"):
            if dtype == "little":
                try:
                    return parse_functions.ltob(data).encode()
                except:
                    return parse_functions.ltob(data)
            else:
                try:
                    return data.encode()
                except:
                    return data
        else: raise ValueError("Datatype must be little or big")
    



class Datatype(Enum): ## used to easily obtain len values
    INT = 4  #integer
    SHORT = 2  #short
    CHAR = 1  #char
    FLOAT = 4  #float
    LONG = 8 #long

class Struct():
        def __init__(self, name, struct_tuple, *substructs):
            r'''Pass the main struct's 2d values tuple into this, and any substructs this uses.
            Second level should look like (name, type, flags)
            
            |Datatype  | Data Field Format                     | Notes                                                                    
            |----------|---------------------------------------|-----------------------------------------------------------|
            | INT      | <integer><flag>                       | Basic type                                                   
            | LONG     | <integer><flag>                       | Basic type                                                  
            | SHORT    | <integer><flag>                       | Basic type                                                   
            | CHAR     | <single char><flag>                   | Basic type                                                   
            | FLOAT    | <float><flag>                         | Basic type                                                  
            | CONST    | <constant>                            | For constant values                                        
            | ARRAY    | <data item>/<repeats>                 | For arrays of basic types or of another substruct   
            | VARLEN   | <RAW/STR>/<previous field/basic type> | For variable length - raw is binary, str is string data 
            
            All basic types use one of the flags UL/SL/UB/SB for (un)signed, little/big endian
            Type-specific flags should not be mixed, care must be taken to keep the proper format for data fields.
            
            Example struct definition:
            main_struct=(("value01", "FLOATUL"),
                ("value02", "substruct/24"),
                ("value03", "ABCD"))
            substruct = ...
            substruct_object = StructMaster.new_struct(substruct)
            main_struct_object = StructMaster.new_struct(main_struct, substruct_object)
            '''

            self.__BASIC_TYPES = Datatype
            self.__BASIC_TYPES_MEMBERS = ["INT", "SHORT", "CHAR", "FLOAT", "LONG"] #Datatype.__members__
            self.__BASIC_FLAGS = ["UL", "SL", "UB", "SB"]
            self.__substructs = [] #array of substruct objects so names can be indexed
            self.struct_name = name #substruct name, so substructs can easily be accessed
            
            for substruct in substructs: #appending all used substruct objects
                self.__substructs.append(substruct)
            self.__struct = struct_tuple
            try:
                self.__is_tuple_valid(struct_tuple)
            except StructError as e:
                raise StructError("An error occurred while defining struct: %s" %(e)) from None

                        
            length = 0
            for dtype in self.__struct:                
                typeident = dtype[1] #the type (e.g. CONST/"ABC", "FLOAT", "SUBSTRUCT"/12)
                is_basic_type = self.__is_basic_type(typeident)
                
                if not(is_basic_type) and "/" in typeident: #for most special types (not consts)
                    data1, data2 = typeident.split("/") #data1 for substructs/arrays/etc, data2 for repeats/varlen type
                elif is_basic_type: #basic types
                    if typeident[:-1] == "CHAR":
                        data1 = typeident[:-1] #if a char (since they only use B/L not U or S)
                    else:
                        data1 = typeident[:-2] #data1 for types (all we care about for length) - this is up to (not incl) flags


                if is_basic_type: #basic type
                    length += self.__BASIC_TYPES[data1].value #enum value for the datatype part
                else:
                    if "/" not in typeident: #constant
                        length += len(typeident)

                    elif data1 in ["RAW", "STR"]: #varlen
                        try:
                            int(data2)
                            length += int(data2)
                        except:
                            pass #field varlen has no defined length at first

                    else: #array
                        arr_typeident = typeident.split("/")[0]
                        arr_repeats = typeident.split("/")[1]
                        is_basic_type = self.__is_basic_type(arr_typeident)
                        if is_basic_type: #basic types
                            if arr_typeident[:-1] == "CHAR":
                                data1 = arr_typeident[:-1] #if a char (since they only use B/L not U or S)
                            else:
                                data1 = arr_typeident[:-2] #data1 for types (all we care about for length) - this is up to (not incl) flags
                        
                        try: #if a standard integer amount of repeats
                            arr_repeats = int(arr_repeats)
                        except: #if datafield repeats, this is not defined yet
                            break
                        
                        if is_basic_type: #basic type in the array
                            length += self.__BASIC_TYPES[data1].value * arr_repeats

                        elif self.__get_substruct(arr_typeident): #if a substruct
                            substruct_len = self.__get_substruct(arr_typeident).struct_len
                            substruct_repeats = int(data2)
                            length += substruct_repeats * substruct_len
                    
            self.__struct_len = length

        def __is_basic_type(self, typeident):
            r'''returns true if it uses <value><flag> formatting, or is a char, and isn't an array
            '''
            return ((typeident[-2:] in self.__BASIC_FLAGS and \
                    typeident[:-2] in self.__BASIC_TYPES_MEMBERS) or\
                    typeident[:-1] == "CHAR") and \
                    "/" not in typeident

        def __is_tuple_valid(self, struct_tuple):
            r'''Pass a tuple of key-value tuples into this, returns True if it is valid
            An invalid struct will have an error raised with information
            '''
            for item in struct_tuple: ##checking if it is a valid struct, tuple by tuple
                
                typeident = item[1] #the type (e.g. CONST/"ABC", "FLOAT", "SUBSTRUCT"/12)
                is_basic_type = self.__is_basic_type(typeident)
                split_bslash = typeident.split("/") #used a lot in the following code, so tuple is pre-made here
                
                if not(is_basic_type) and "/" in typeident: #for most special types (not consts)
                    data1, data2 = typeident.split("/") #data1 for substructs/arrays/etc, data2 for repeats/varlen type
                elif is_basic_type: #basic types
                    data1 = typeident[:-2] #data1 for types (all we care about for length) - this is up to (not incl) flags



                if len(item) != 2: #if not two fields
                    raise StructError("Invalid structure length: \"%s\" has not got two items"
                                        %(item[0], ))
                
                elif item[0] in self.__BASIC_TYPES_MEMBERS:
                    raise StructError("Invalid field name \"%s\": shares a basic datatype's name"
                                      %(item[0], ))

                elif "/" in typeident: #if an array or varlen
                    try:
                        if int(split_bslash[1]) < 1: raise StructError("Invalid repeats in array \"%s\": \"%s\""
                                                                                                    %(item[0], split_bslash[1]))#if number of repeats
                    except: #no chars/etc etc unless another field's name
                        is_valid = False
                        for item_definition in struct_tuple:
                            is_valid = (split_bslash[1] == item_definition[0] and item_definition[1][:-2] in ["INT", "LONG", "SHORT"])
                            #is_valid is a bool, true if the referenced data field exists and is an int, long, or short.

                            if item[0] == item_definition[0] or is_valid == True: break #up until the array's name
                        if not is_valid: raise StructError("Invalid repeats field specified in array \"%s\""
                                                                                                      %(item[0]))
                if (split_bslash[0][:-2] in self.__BASIC_TYPES_MEMBERS \
                    and split_bslash[0][-2:] in self.__BASIC_FLAGS) \
                    or split_bslash[0][:-1] == "CHAR" \
                    or split_bslash[0] in ["RAW", "STR"] \
                    or not("/" in typeident): #if an array, varlen, const, or basic type
                    pass
                else: #if a substruct array
                    if not self.__get_substruct(split_bslash[0]): raise StructError("Invalid substruct specified in array: Substruct \"%s\""
                                                                                                                                        %(split_bslash[0]))#if an invalid substruct-using array
            return True

        @property
        def struct_len(self):
            r'''returns the substruct's length, calculates it first if not done already,
            note that if using varlens, this will be a minimum length as varlens have a theoretically infinite size
            '''
            return self.__struct_len

        @property
        def struct(self):
            r'''returns the struct tuple
            '''
            return self.__struct #tuple so no risk of editing

        @property
        def substructs(self):
            r'''returns a copy of the substruct array
            '''
            return self.__substructs.copy()

        
        def __get_substruct(self, substruct_name):
            r'''returns a substruct's object from a string reference, from the substruct dict
            '''
            for substruct in self.__substructs:
                if substruct.struct_name == substruct_name:
                    return substruct
            return None #if none found

        def __parse_basic_types(self, fp, typeident):
            r'''parses basic types, returns the output and increments the file pointer supplied.
            '''
            if typeident[:-1] == "CHAR":
                typeident_split_flag = typeident[:-1]
            else:
                typeident_split_flag = typeident[:-2]
            item_size = self.__BASIC_TYPES[ typeident_split_flag ].value

            if typeident_split_flag in ["INT", "LONG", "SHORT"]: #one of the int types
                output = parse_functions.btoi(fp.read(item_size))

            elif typeident_split_flag == "FLOAT": #floats
                output = parse_functions.btof(fp.read(item_size))

            else: #chars
                output = parse_functions.btot(fp.read(item_size))

            return output

        def __pack_basic_types(self, fp, data, typeident):
            r'''packs basic types, pass in the file pointer, the data to be written, and its typeident.
            '''
            if typeident[:-1] == "CHAR":
                typeident_split_flag = typeident[:-1]
            else:
                typeident_split_flag = typeident[:-2]

            if typeident_split_flag in ["INT", "LONG", "SHORT"]: #one of the int types
                output = parse_functions.itob(data, length=self.__BASIC_TYPES[typeident_split_flag].value)

            elif typeident_split_flag == "FLOAT": #floats
                output = parse_functions.ftob(data)

            else: #chars
                output = parse_functions.ttob(data)

            fp.write(output)
        


        def parse(self, fp):
            r'''Pass a file object, it will be interpreted based on this object's struct.
            The function will return nested dictionaries of parsed values
            The values returned will be automatically converted to their respective type
            '''
            ##########
            ## Set up proper big and little endian stuff for this, and signed datatypes
            ##########
            ##########
            ## Set up over/underflowing on the provided data?
            ## For this, potentially return -1 for too little data, 0 for exact, 1 for too much data - this would allow an easy way for end user to check which.
            ## Field (name) + repeat that encountered no data could also be returned
            ##########
            
            output = {} #main data output
            
            for dtype in self.__struct:
                nameident = dtype[0] #the name (e.g. fourCC, version)
                typeident = dtype[1] #the type (e.g. CONST/ABC, FLOAT)
                typeident_sb = typeident.split("/") #used often so set here for ease of use
                is_basic_type = self.__is_basic_type(typeident)
                                    #if it uses <value><flag> formatting, and isn't an array
                if is_basic_type:
                    if typeident[:-1] == "CHAR":
                        typeident_split_flag = (typeident[:-1], typeident[-1:])
                    else:
                        typeident_split_flag = (typeident[:-2], typeident[-2:])

                ## parse the data ##
                if is_basic_type:
                    output[nameident] = self.__parse_basic_types(fp, typeident)

                elif not(is_basic_type) and "/" not in typeident: #constants
                    item_size = len(typeident)
                    data_item = fp.read(item_size).decode()

                    if data_item != typeident:
                        raise StructError("Value %r does not match predefined constant %r"
                                            %(data_item, typeident))
                    
                    output[nameident] = typeident


                elif "/" in typeident: #if an array or varlen
                    if typeident_sb[0] in ["RAW", "STR"]: #for varlen
                        varlen_typeident = typeident_sb[0]
                        try:
                            varlen_len = int(typeident_sb[1])
                        except:
                            varlen_len = output[typeident_sb[1]] #index into the output dictionary
                        
                        if varlen_typeident == "RAW": #raw binary
                            output[nameident] = fp.read(varlen_len)
                        elif varlen_typeident == "STR": #string
                            output[nameident] = parse_functions.btot(fp.read(varlen_len), "big")
                        else:
                            raise StructError("Error encountered while parsing varlen \"%s\" \"%s\"" %(nameident, typident))

                    else: #arrays of datatypes
                        arr_typeident = typeident_sb[0]
                        output_tmp = []
                        is_basic_type = self.__is_basic_type(arr_typeident)
                        
                        try: #if integer repeats
                            arr_repeats = int(typeident_sb[1])
                        except: #if datafield repeats
                            arr_repeats = int(output[typeident_sb[1]])
                        
                        if is_basic_type:
                            for x in range(arr_repeats):
                                output_tmp.append(self.__parse_basic_types(fp, arr_typeident))

                        elif self.__get_substruct(arr_typeident):
                            for x in range(arr_repeats):
                                output_tmp.append(self.__get_substruct(arr_typeident).parse(fp))

                        output[nameident] = output_tmp
                        
            return output

            
        def pack(self, fp, data_array, overwrite_bytes=0):
            r'''
            Pass in a file object, file pointer set to the location's beginning, and the data
            Data should be in the format of a 2d list with sublists for each repeat, e.g. [[123, "ABC", ["12", "34"]],], or a similarly formatted dictionary.
            The data will be encoded and written to the file object, at the current file pointer location.
            Overwrite bytes means that X amount of bytes will be overwritten if set. Default is 0
            '''
            writepos = fp.tell()
            with tempfile.TemporaryFile() as tf:
                ## I'm writing to the temporary file as you can't insert midway through a python file
                ## Instead I write all up to the writepos (fp is at the start of the location to be written) to the temporary file, then write the new data, then write everything left in the original file
                ## after that, I write the temporary file contents back to the main file
                fp.seek(0) #start of the file
                tf.write(fp.read(writepos)) #write everything before the new data into the file

                index = -1 #tracking where is being worked on
                cdata = None #current piece of data
                if type(data_array) == dict:
                    data_array = [data_array,]
                else:
                    if type(data_array[0]) not in (dict, list):
                        data_array = [data_array,]
                for data in data_array:
                    for dtype in self.__struct:
                        nameident = dtype[0] #the name (e.g. fourCC, version)
                        typeident = dtype[1] #the type (e.g. CONST/ABC, FLOAT)
                        typeident_sb = typeident.split("/")
                        is_basic_type = self.__is_basic_type(typeident)
                                            #if it uses <value><flag> formatting, and isn't an array
                        if is_basic_type:
                            typeident_split_flag = (typeident[:-2], typeident[-2:])
                            if typeident[:-1] == "CHAR":
                                typeident_split_flag = (typeident[:-1], typeident[-1:])
                                
                        index += 1
                        if type(data) == list:
                            cdata = data[index]
                        else:
                            cdata = data[nameident]

                        ## pack the data ##
                        if type(cdata) not in [int, set, list, dict] and typeident[:4] == "RAW/" and cdata[:5] == "PATH/":
                            path = cdata.split("/", 1)[1]
                                
                            with open(path, "rb") as data:
                                while True:
                                    chunk = data.read(1 << 14)
                                    if not chunk:
                                        break
                                    tf.write(chunk)
                                break

                            
                        if is_basic_type: #basic types
                            self.__pack_basic_types(tf, cdata, typeident)


                        elif not(is_basic_type) and "/" not in typeident: #constants
                            if cdata == typeident:
                                try:
                                    tf.write(str(cdata).encode())
                                except AttributeError:
                                    tf.write(str(cdata))
                            else: raise IOError("%s does not match predefined constant %s" %(cdata, typeident))


                        elif "/" in typeident: #if an array or varlen
                                
                            if typeident_sb[0] == "RAW": #varlen raw binary
                                try:
                                    tf.write(str(cdata).encode())
                                except AttributeError:
                                    tf.write(str(cdata))
                                    
                            elif typeident_sb[0] == "STR": #varlen string
                                tf.write(parse_functions.ttob(cdata, "big"))
                                parse_functions.ttob(cdata, "big")
                            
                            else: #arrays of datatypes
                                arr_typeident = typeident_sb[0]
                                is_basic_type = self.__is_basic_type(arr_typeident)

                                try: #if a standard integer amount of repeats
                                    arr_repeats = int(typeident_sb[1])
                                except: #if datafield repeats
                                    arr_repeats = int(data[typeident_sb[1]]) ##### check this later; is it fetching the right len? #####

                                if is_basic_type:
                                    for x in range(arr_repeats):
                                        try:
                                            self.__pack_basic_types(tf, cdata[x], arr_typeident)
                                        except:
                                            self.__pack_basic_types(tf, cdata[x].encode(), arr_typeident)

                                elif self.__get_substruct(arr_typeident):
                                    for x in range(arr_repeats):
                                        self.__get_substruct(arr_typeident).pack(tf, cdata[x])

                
                # fp currently initialised to writepos
                # tf currently initialised to writepos + length of the data written
                origpos = tf.tell() #writepos + length of data written
                fp.seek(overwrite_bytes, 1) #seeks ahead by overwrite bytes amount, this lets OBs be ignored in the read 
                tf.write(fp.read()) #rest of file
                tf.seek(0)

                fp.seek(0)
                fp.truncate() #clear fp

                fp.write(tf.read()) #copy back data, with new data now inserted
                fp.seek(origpos) #seek pointer to end of newly written data
                

                

