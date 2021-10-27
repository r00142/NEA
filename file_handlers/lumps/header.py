from .structure_parser import Struct

lumps = Struct("lumps",
                (("fileofs", "INTUL"),
                ("filelen", "INTUL"),
                ("version", "INTUL"),
                ("fourCC", "CHARL/4")))

header = Struct("header",
                (("ident", "VBSP"),
                ("version", "INTUL"),
                ("lump_t", "lumps/64"),
                ("revision", "INTUL",)),
                lumps)


class HeaderParser():
    def __init__(self, fp):
        self.__fp = fp
    
    def parse(self):
        self.__fp.seek(0)
        return header.parse(self.__fp)

    def get_single_lumpt(self, lump_num: int):
        r'''returns lump file offset, len, version, fourcc
        '''
        return self.parse()["lump_t"][lump_num]

class HeaderPacker():
    def __init__(self, fp):
        self.__fp = fp

    def pack(self, data):
        self.__fp.seek(0)
        header.pack(self.__fp, [data,], 1036)
