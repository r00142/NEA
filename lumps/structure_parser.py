from enum import Enum
try:
    from shared import *
except:
    from .shared import *


class Datatype(Enum):
    INT = 4  #integer
    SHORT = 2  #short
    CHAR = 1  #char
    FLOAT = 4  #float
    LONG = 8 #long

class Flags(Enum):
    SUB = 0 #substruct
    UL = 1 #unsigned little
    SL = 2 #signed little
    UB = 3 #unsigned big
    SB = 4 #signed big
    CN = 5 #constant
    ARR = 6 #array of basic datatypes of a fixed length
    VAR = 7 #variable length field, set to the value of another item (int or short)

class StructError(Exception):
    '''Error within a structure definition
    '''
    pass


class Struct():
        def __init__(self):
            self.__structdict = {} #dictionary of all the structure object's structs
            self.__structlendict = {} #dictionary of all the structure object's structs' lengths
                
        def __lencalc(self, struct_name):
            length = 0

            for dtype in  range(len(self.__structdict[struct_name])):
                typeident = self.__structdict[struct_name][dtype][1] #the type (e.g. CONST/ABC, FLOAT)
                flagident = self.__structdict[struct_name][dtype][2] #the flag(e.g. CN, UL)
                
                if typeident in Datatype.__members__ and flagident not in ["CN", "SUB", "ARR", "VAR"]: #normal types
                    length += Datatype[typeident].value
                    
                elif flagident == "CN": #constant
                    length += len(typeident.split("/")[1])

                elif flagident == "ARR": #array
                    length += int(typeident.split("/")[1]) * Datatype[typeident.split("/")[0]].value
                    
                elif flagident == "SUB": #substruct
                    if self.__structlendict[typeident.split("/")[0]] == -1: #if substruct length not yet set
                        self.__lencalc(typeident.split("/")[0])

                    substruct_size = self.__structlendict[typeident.split("/")[0]] #length of the struct
                    substruct_repeats = int(typeident.split("/")[1]) #amount of repeats of the struct
                    length += substruct_size*substruct_repeats

                elif flagident == "VAR": #varlen
                    pass #varlen has no defined length at first
                    
            self.__structlendict[struct_name] = length
            

        def new_struct(self, name, struct_tuple):
                r'''Pass the struct's name and a 2d tuple of values into this
                Second level should look like (name, type, flags)
                
                | Datatype | Data Field Format         | Special flags | Notes                                                   |           
                |----------|---------------------------|---------------|---------------------------------------------------------|
                | INT      | <integer>                 | None          | Basic type                                              |
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
                    ("value03", "CONST/"ABCD", "CN"))
                StructMaster.new_struct("Main Structure", main_struct)
                '''
                for item in struct_tuple: ##checking if it is a valid struct
                    if len(item) != 3: #if not three fields
                        raise StructError("Invalid structure length in \"%s\": \"%s\" has not got three items" %(name, item))

                    elif item[1] not in Datatype.__members__ and item[2] not in ["SUB","CN","ARR","VAR"]: #if not a valid datatype
                        raise StructError("Invalid datatype specified in \"%s\": \"%s\"" %(name, item[1]))

                    elif item[2] == "SUB": #if too few repeats on a substruct
                        try:
                            if int(item[1].split("/")[1]) < 1: #if an invalid substruct
                                raise StructError("Invalid amount of substructs in \"%s\": \"%s\"" %(name, item[1]))
                        except: #originally no floats, now no chars etc
                            raise StructError("Invalid amount of substructs in \"%s\": \"%s\"" %(name, item[1]))
                        ## FIX THIS LATER - SUBSTRUCTS CAN DRAW OFF of OTHER VARIABLE CONTENTS LIKE VARLENS##

                    elif item[2] == "SUB"and item[1].split("/")[0] not in self.__structdict: #if an invalid substruct
                        raise StructError("Invalid substruct specified in \"%s\": Substruct \"%s\"" %(name, item[1].split("/")[0]))
                    
                    elif item[2] not in Flags.__members__: #if an invalid flag
                        raise StructError("Invalid flag specified in \"%s\": \"%s\"" %(name, item[2]))

                    elif name in self.__structdict: #name exists already
                        raise StructError("Invalid substruct name \"%s\": already exists in structure dictionary" %(name, name))

                    elif "/" not in item[1] and item[2] in ["SUB", "CN", "ARR","VAR"]: #incorrectly formatted const/substruct
                        raise StructError("Invalid const, substruct, array, or varlen in \"%s\": \"%s\"" %(name, item[1]))

                    elif item[2] == "SUB" and item[1].split("/")[1] in Datatype.__members__: #substruct called a basic datatype
                        raise StructError("Invalid substruct name in \"%s\": \"%s\" shares a basic datatype's name" %(name, item[1]))

                    elif item[1].split("/")[0] not in Datatype.__members__ and item[2] == "ARR": #invalid array datatype
                        raise StructError("Invalid datatype specified in \"%s\": array \"%s\"" %(name, item[1]))

                    elif item[2] == "VAR" and item[1].split("/")[0] not in ["RAW", "STR"]: #invalid varlen
                        raise StructError("Invalid type specified in \"%s\": varlen \"%s\" - must be RAW or STR" %(name, item[1]))

                    elif item[2] == "VAR": #varlen without a valid field to link to
                        is_valid = False
                        for item_definition in struct_tuple:
                            if item[1].split("/")[1] == item_definition[0]:
                                is_valid = True
                            elif item[0] == item_definition[0]:
                                break
                        if not is_valid:
                            raise StructError("Invalid field specified in \"%s\": varlen \"%s\" does not have a previous valid field linking to it"%(name, item[1]))
                    
                self.__structdict[name] = struct_tuple
                self.__structlendict[name] = -1 #defined in lencalc

        def getlen(self, struct_name):
            if self.__structlendict[struct_name] == -1:
                self.__lencalc(struct_name)
            return self.__structlendict[struct_name]
        
        def getstructdict(self):
            return self.__structdict.copy()               
                    

        def parse(self, data, struct_name, repeats=1, is_substruct=False):
            '''Pass binary data into this, it will be interpreted based on the structure set up
            The function will return a tuple of parsed values
            The values returned will be automatically converted to their respective type
            Ignore 'repeats' and 'is_substruct', they are internal arguments
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
            for x in range(repeats): #repeats is mostly used for substructs
                for dtype in  range(len(self.__structdict[struct_name])):
                    nameident = self.__structdict[struct_name][dtype][0] #the name (e.g. fourCC, version)
                    typeident = self.__structdict[struct_name][dtype][1] #the type (e.g. CONST/ABC, FLOAT)
                    flagident = self.__structdict[struct_name][dtype][2] #the flag(e.g. CN, UL)]
                    
                    if typeident in ["INT", "LONG", "SHORT"]: #one of the int types            
                        output[nameident] = btoi_ul(data[:Datatype[typeident].value])
                        data = data[Datatype[typeident].value:]

                    elif typeident == "FLOAT": #floats
                        output[nameident] = btof_ul(data[:Datatype[typeident].value])
                        data = data[Datatype[typeident].value:]

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
                                output_tmp.append(btoi_ul(data[:Datatype[arr_typeident].value]))
                                data = data[Datatype[arr_typeident].value:]

                        else: #for char
                            for item in range(arr_repeats):
                                if data[:Datatype[arr_typeident].value] == b"\x00": #null string check
                                    output_tmp.append("")
                                else:
                                    output_tmp.append(btot_l(data[:Datatype[arr_typeident].value]))
                                data = data[Datatype[arr_typeident].value:]

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

                        data, substruct_output = self.parse(data, substruct_name, substruct_repeats, True)

                        if substruct_name not in output: #nonexistent substruct
                            output[substruct_name] = []
                            
                        output[substruct_name]= substruct_output
                        ### currently isn't properly creating new entries in arrays

                        
                    else: #the other datatypes
                        output[nameident] = btot_l(data[:Datatype[typeident].value])
                        data = data[Datatype[typeident].value:]

                output_arr.append(output.copy())

            if is_substruct == True:
                return(data, output_arr)
            else:
                output_final = {}
                output_final[struct_name] = output
            
                return output_final

            
        def pack(self, data):
            pass       

