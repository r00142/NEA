from enum import Enum
try:
    from shared import *
except:
    from .shared import *

class StructError(Exception):
    '''Error within a structure definition
    '''
    pass

class Struct():
        def __init__(self):
            class __Datatype(Enum): ## used to easily obtain len values
                INT = 4  #integer
                SHORT = 2  #short
                CHAR = 1  #char
                FLOAT = 4  #float
                LONG = 8 #long
            self.__struct_dict = {} #dictionary of all the structure object's structs
            self.__struct_len_dict = {} #dictionary of all the structure object's structs' lengths
            self.__basic_types = __Datatype
            self._basic_types_members = self.__Datatype.__members__
            self.__basic_flags = ["UL", "SL", "UB", "SB"]
            
        def __lencalc(self, struct_name):
            length = 0

            for dtype in range(len(self.__struct_dict[struct_name])):     
                typeident = self.__struct_dict[struct_name][dtype][1] #the type (e.g. CONST/"ABC", "FLOAT", "SUBSTRUCT"/12)
                is_basic_type = typeident[-2:] in self.__basic_flags and
                                len(typeident.split("/") == 1 #if it uses <value><flag> formatting, and isn't an array

                if not(is_basic_type) and len(typeident.split("/") > 1: #for most special types (not consts)
                    data1, data2 = typeident.split("/") #data1 for substructs/arrays/etc, data2 for repeats/varlen type
                elif is_basic_type: #basic types
                    data1 = typeident[:-2] #data1 for types (all we care about for length) - this is up to (not incl) flags

                if is_basic_type: #basic type
                    length += self.__basic_types[data1].value #enum value for the datatype part

                else:
                    elif len(typeident.split("/") == 1: #constant
                        length += len(typeident)
                                   
                    elif data1[:-2] in self._basic_types_members: #array
                        array_type_len = self.__basic_types[ data1[:-2] ].value #length of the type used (bytes)
                        array_repeats = int(data2) #repeats of the basic type
                        length += array_type_len * array_repeats

                    ##
                    elif not(is_basic_type) and data1 in self.__struct_dict: #substruct
                        #data1 =  substruct name, data2 = repeats
                        substruct_size = self.get_len(data1) #length of the substruct, auto lencalcs if not defined
                        substruct_repeats = int(data2) #amount of repeats of the struct
                        length += substruct_size * substruct_repeats
                    ##

                    elif data2 == "STR" or data2 == "RAW": #varlen
                        pass #varlen has no defined length at first
                    
            self.__struct_len_dict[struct_name] = length

        def __is_tuple_valid(self, struct_tuple):
            r'''Pass a struct tuple into this, returns True if it is valid
            An invalid struct will have an error raised with information
            '''
            for item in struct_tuple: ##checking if it is a valid struct
                if len(item) != 3: #if not three fields
                    raise StructError("Invalid structure length: \"%s\" has not got three items" %(item, ))

                elif item[0] in self.__basic_types.__members__:
                    raise StructError("Invalid field name \"%s\": shares a basic datatype's name" %(item, ))

                elif item[1] not in self.__basic_types.__members__ and item[2] not in self.__special_flags: #if not a valid datatype
                    raise StructError("Invalid datatype specified: \"%s\"" %(item[1]))

                elif item[2] == "SUB": #if too few repeats on a substruct
                    try:
                        if int(item[1].split("/")[1]) < 1: #if number of repeats
                            raise StructError("Invalid repeats in substruct: \"%s\"" %(item[1]))
                    except: #originally no floats, now no chars etc
                        raise StructError("Invalid repeats in substruct: \"%s\"" %(item[1]))
                    ## REDO THIS LATER - SUBSTRUCTS CAN DRAW OFF OF OTHER VARIABLE CONTENTS LIKE VARLENS##

                elif item[2] == "SUB"and item[1].split("/")[0] not in self.__struct_dict: #if an invalid substruct
                    raise StructError("Invalid substruct specified: Substruct \"%s\"" %(item[1].split("/")[0]))
                
                elif item[2] not in (self.__basic_flags + self.__special_flags): #if an invalid flag
                    raise StructError("Invalid flag specified: \"%s\"" %(item[2]))

                elif "/" not in item[1] and item[2] in self.__special_flags: #incorrectly formatted const/substruct
                    raise StructError("Invalid const, substruct, array, or varlen: \"%s\"" %(item[1]))

                elif item[2] == "SUB" and item[1].split("/")[1] in self.__basic_types.__members__: #substruct called a basic datatype
                    raise StructError("Invalid substruct name: \"%s\" shares a basic datatype's name" %(item[1]))

                elif item[1].split("/")[0] not in self.__basic_types.__members__ and item[2] == "ARR": #invalid array datatype
                    raise StructError("Invalid datatype specified: array \"%s\" must use a basic type" %(item[1]))

                elif item[2] == "VAR" and item[1].split("/")[0] not in ["RAW", "STR"]: #invalid varlen
                    raise StructError("Invalid type specified: varlen \"%s\" - must be RAW or STR" %(item[1]))

                elif item[2] == "VAR": #varlen without a valid field to link to
                    is_valid = False
                    for item_definition in struct_tuple:
                        if item[1].split("/")[1] == item_definition[0]:
                            is_valid = True
                        elif item[0] == item_definition[0]: #up until the varlen's name
                            break
                    if not is_valid:
                        raise StructError("Invalid field specified: varlen \"%s\" does not have a previous valid field linking to it"
                                          %(item[1]))
            return True

        def new_struct(self, name, struct_tuple):
                r'''Pass the struct's name and a 2d tuple of values into this.
                Second level should look like (name, type, flags)
                
                |Datatype | Data Field Format         | Special flags | Notes                                                   |           
                |----------|---------------------------|---------------|---------------------------------------------------------|
                | INT       | <integer>                 | None          | Basic type                                              |
                | LONG     | <integer>                 | None          | Basic type                                              |
                | SHORT    | <integer>                 | None          | Basic type                                              |
                | CHAR     | <single char>             | None          | Basic type                                              |
                | FLOAT    | <float>                   | None          | Basic type                                              |
                | CONST    | CONST/<constant>          | CN            | For constant values                                     |
                | SUBSTRUCT| <substruct>/<repeats>     | SUB           | For substructures                                       |
                | ARRAY    | <basic type>/<repeats>    | ARR           | For arrays of basic types                               |
                | VARLEN   |<RAW/STR>/<previous field> | VAR           | For variable length - raw is binary, str is string data |
                
                All basic types use one of the flags UL/SL/UB/SB for (un)signed, little/big endian
                Type-specific flags should not be mixed, care must be taken to keep the proper format for data fields.
                
                Example struct defintion:
                main_struct=(("value01", "FLOAT", "SL"),
                    ("value02", "substruct/24", "SUB"),
                    ("value03", "CONST/ABCD", "CN"))
                StructMaster.new_struct("Main Structure", main_struct)
                '''
                try:
                    self.__is_tuple_valid(struct_tuple)
                    
                    if name in self.__struct_dict: #name exists already
                        raise StructError("Invalid struct name \"%s\": already exists in structure dictionary" %(name, name))

                except StructError as e:
                    raise StructError("An error occurred while defining struct \"%s\": %s" %(name, e)) from None

                    
                self.__struct_dict[name] = struct_tuple
                self.__struct_len_dict[name] = -1 #defined via lencalc, we set this to -1 on every change

        def add_field(self):
            pass

        def delete_field(self):
            pass

        def update_field(self, struct, field_to_replace, updated_tuple):
            try:
                structure = self.__struct_dict[struct]
            except KeyError as e:
                raise KeyError("Invalid structure \"%s\" specified" %struct)
            try:
                for field in structure:
                    if field[0] == field_to_replace:
                        index = structure.index(field) #to obtain the index of the field
                        structure[index] = updated_tuple #we can then modify directly
            except KeyError as e:
                raise KeyError("Invalid field name \"%s\" specified" %field_to_replace)

            try:
                self.__is_tuple_valid((updated_tuple, )) #checking if it is a valid edit or not
            except StructError as e:
                raise StructError("Invalid tuple formatting: %s" %e) from None 
            
        def delete_struct(self):
            pass

        def update_struct(self):
            pass

        def get_len(self, struct_name):
            """
            returns the substruct's length, calculates it first if not done already,
            note that if using varlens, this will be a minimum length as varlens have a theoretically infinite size"""
            if self.__struct_len_dict[struct_name] == -1:
                self.__lencalc(struct_name)
            return self.__struct_len_dict[struct_name]
        
        def get_struct_dict(self):
            '''returns a copy of the struct dictionary
            '''
            return self.__struct_dict.copy()

        
                    

        def parse(self, data, struct_name):
            '''Pass binary data into this, it will be interpreted based on the struct set up.
            The function will return a set of nested dictionaries of parsed values
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
            output_arr = [] #temporary, for substructs
            
            for dtype in  range(len(self.__struct_dict[struct_name])):
                nameident = self.__struct_dict[struct_name][dtype][0] #the name (e.g. fourCC, version)
                typeident = self.__struct_dict[struct_name][dtype][1] #the type (e.g. CONST/ABC, FLOAT)
                flagident = self.__struct_dict[struct_name][dtype][2] #the flag(e.g. CN, UL)]
                
                if typeident in ["INT", "LONG", "SHORT"]: #one of the int types            
                    output[nameident] = btoi_ul(data[:self.__basic_types[typeident].value])
                    data = data[self.__basic_types[typeident].value:]

                elif typeident == "FLOAT": #floats
                    output[nameident] = btof_ul(data[:self.__basic_types[typeident].value])
                    data = data[self.__basic_types[typeident].value:]

                elif flagident == "CN": #constants
                    constval = typeident.split("/")[1]
                    if data[:len(constval)].decode() != constval:
                        raise StructError("Constant %s does not match predefined constant %s"
                                            %(data[:len(constval)].decode(), constval))
                    
                    output[nameident] = constval
                    data = data[len(constval):]

                elif flagident == "ARR": #arrays of datatypes
                    arr_typeident = typeident.split("/")[0]
                    arr_repeats = int(typeident.split("/")[1])
                    output_tmp = []
                    
                    if arr_typeident in ["INT", "FLOAT", "LONG", "SHORT"]: #one of the int types
                        for item in range(arr_repeats):
                            output_tmp.append(btoi_ul(data[:self.__basic_types[arr_typeident].value]))
                            data = data[self.__basic_types[arr_typeident].value:]

                    else: #for char
                        for item in range(arr_repeats):
                            if data[:self.__basic_types[arr_typeident].value] == b"\x00": #null string check
                                output_tmp.append("")
                            else:
                                output_tmp.append(btot_l(data[:self.__basic_types[arr_typeident].value]))
                            data = data[self.__basic_types[arr_typeident].value:]

                    output[nameident] = output_tmp

                elif flagident == "VAR": #variable length
                    varlen_typeident = typeident.split("/")[0]
                    varlen_len = output[typeident.split("/")[1]]
                    
                    if varlen_typeident == "RAW": #raw binary
                        output[nameident] = data[:varlen_len]
                    elif varlen_typeident == "STR": #string
                        output[nameident] = btot_b(data[:varlen_len])
                    else:
                        raise StructError("Issue with parsing varlen \"%s\" \"%s\"" %(nameident, typident))
                        
                    data = data[varlen_len:]

                elif flagident == "SUB": #substructs 
                    substruct_name = typeident.split("/")[0]
                    substruct_repeats = int(typeident.split("/")[1])
                    substruct_output = []
                    
                    for x in range(substruct_repeats):
                        substruct_output.append(self.parse(data, substruct_name))
                        data = data[self.get_len(substruct_name):] #to iteratively cut the data as it progresses

                    output[substruct_name]= substruct_output

                else: #the other datatypes
                    output[nameident] = btot_l(data[:self.__basic_types[typeident].value])
                    data = data[self.__basic_types[typeident].value:]

            return output

            
        def pack(self, data):
            pass       

##if __name__ == "__main__":
##    x = Struct()
##    lumpsformat = [("fileofs", "INT", "UL"),
##                    ("filelen", "INT", "UL"),
##                    ("version", "INT", "UL"),
##                    ("fourCC", "CHAR/4", "ARR")]
##    x.new_struct("mainstruct", lumpsformat)
##    
##    x.update_field("mainstruct", "filelen", ("filelen2", "CONST/VBSP", "CN"))
##    print(x.get_struct_dict())

