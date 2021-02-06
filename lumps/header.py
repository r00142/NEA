try:
    from structure_parser import *
except:
    from .structure_parser import *



#bsp = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf\\maps\\lump40_format_testing.bsp"
#bsp = "l40_testing\\lump40_format_testing.bsp"


class HeaderParser():
    def __init__(self, bsp_input):
        #first 1036 bytes of the file are always the header
        with open(bsp_input, "rb", 1036) as bsp_file:
            self.__bsp_header = bsp_file.read(1036)
            
        self.__StructMaster = Struct()

        lumpsformat = (("fileofs", "INT", "UL"),
                    ("filelen", "INT", "UL"),
                    ("version", "INT", "UL"),
                    ("fourCC", "CHAR/4", "ARR"))
        self.__StructMaster.new_struct("lumps", lumpsformat)

        headerformat = (("ident", "CONST/VBSP", "CN"),
                    ("version", "INT", "UL"),
                    ("lump_t", "lumps/64", "SUB"),
                    ("revision", "INT", "UL"))
        self.__StructMaster.new_struct("header", headerformat)

        self.__header_parsed = self.__StructMaster.parse(self.__bsp_header, "header")

    def get_header_data(self):
        return self.__header_parsed.copy()

    def get_len(self):
        return self.__StructMaster.getlen("header")
        
    def get_all_lumpt(self):
        pass

    def get_single_lumpt(self):
        pass
##
##x = HeaderParser(bsp)
##y = x.get_header_data()
##print(y)
##
##print(x.get_len())
