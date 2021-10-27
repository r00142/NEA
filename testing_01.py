import unittest
##from lumps.header import *
from file_handlers.lumps.structure_parser import *

with open("test_data.bin", "wb") as fp:
    fp.write(b"\x16\x00\x00\x00\x08\x00\x08\x00\x12\x01\x10\x00\x00\x00\x00\x00\x00\x00\x09\x00\x08\x00\x13\x01\x11\x00\x00\x00\x00\x00\x00\x00")
    #data for test_substruct
    fp.write(b"\x54\x4d\x50\x01\x00\x00\x00\x02\x00")
    #data for test_const
    fp.write(b"\x08\x00\x00\x00\x12\x02\x22\x10\x75\x83\x13\x01\x22\x00\x20\x86\x92\x02\x53\x02")
    #data for test_arr
    fp.write(b"\x20\x01\x00\x00\x32\x00\x37\x00\x00\x41\x18\x18\x00\x00\x00\x00\x00\x00\x00\x54\x4d\x50")
    #data for test_parse_basic
    fp.write(b"\x08\x00\x00\x00\x10\x20\x40\x80\x01\x02\x04\x08")
    #data for test_varlen_raw
    fp.write(b"\x04\x00\x00\x00\x54\x4d\x50\x54\x58\x54\x31\x32")
    #data for test_varlen_str
    fp.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    #data for test_parse_nul


class TestStructs(unittest.TestCase):
    def test_basic01(self):
        x = (("int", "INTUL"),
             ("short", "SHORTUL"),
             ("long", "LONGSL"))
        self.substruct01 = Struct("substruct01", x)
        self.assertEqual(self.substruct01.struct, x)

    def test_substruct(self):
        x = (("int", "INTUL"),
             ("short", "SHORTUL"),
             ("long", "LONGSL"))
        self.substruct01 = Struct("substruct02", x)
        
        y = (("int", "INTUL"),
             ("array", "substruct02/2"))
        self.mainstruct = Struct("mainstruct01", y, self.substruct01)
        
        fp.seek(0, 0) # data = 22 524296 274 16 524297 275 17 in hex, 32 bytes in length
        # data = b"\x16\x00\x00\x00\x08\x00\x08\x00\x12\x01\x10\x00\x00\x00\x00\x00\x00\x00\x09\x00\x08\x00\x13\x01\x11\x00\x00\x00\x00\x00\x00\x00"

        self.assertEqual(self.mainstruct.parse(fp),
                         {'int': 22, 'array': [{'int': 524296, 'short': 274, 'long': 16},
                                                                      {'int': 524297, 'short': 275, 'long': 17}]})

    def test_const(self):
        x = (("constant", "TMP"),
             ("int", "INTUL"),
             ("short", "SHORTUL"))
        self.construct01 = Struct("conststruct01", x)
        fp.seek(32, 0) # TMP12 in hex, 32 bytes into file, 9 bytes in length
        # data = b"\x54\x4d\x50\x01\x00\x00\x00\x02\x00"

        self.assertEqual(self.construct01.parse(fp),
                         {'constant': 'TMP', 'int': 1, 'short': 2})
        
    def test_arr(self):
        x = (("int", "INTUL"),
             ("array", "SHORTUL/8"))
        self.arrstruct01 = Struct("arrstruct01", x)
        fp.seek(32 + 9, 0)# 8 530 4130 33653 275 34 34336 658 595 in hex, 20 bytes in length
        #data = b"\x08\x00\x00\x00\x12\x02\x22\x10\x75\x83\x13\x01\x22\x00\x20\x86\x92\x02\x53\x02"
        
        self.assertEqual(self.arrstruct01.parse(fp),
                         {'int': 8, 'array': [530, 4130, 33653, 275, 34, 34336, 658, 595]})

    def test_parse_basic(self): #all basic types
        x = (("int", "INTUL"),
             ("short", "SHORTUL"),
             ("char", "CHARL"),
             ("float", "FLOATUL"),
             ("long", "LONGUL"),
             ("const", "TMP"))
        self.allstruct01 = Struct("allstruct01", x)
        fp.seek(32 + 9 + 20, 0)# 288 50 7 9.5 17 TMP in hex, 22 bytes in length
        #data = b"\x20\x01\x00\x00\x32\x00\x37\x00\x00\x41\x18\x18\x00\x00\x00\x00\x00\x00\x00\x54\x4d\x50"
        
        self.assertEqual(self.allstruct01.parse(fp),
                            {'int': 288, 'short': 50, 'char': '7',
                            'float': 9.5, 'long': 24, 'const': 'TMP'})
        
    def test_get_len(self):
        x = (("fileofs", "INTUL"),
            ("filelen", "INTUL"),
            ("version", "INTUL"),
            ("fourCC", "CHARL/4"))
        self.substruct = Struct("substruct", x)
        #16 bytes long

        y = (("ident", "VBSP"),
                    ("version", "INTUL"),
                    ("lump_t", "substruct/64"),
                    ("revision", "INTUL"))
        self.mainstruct = Struct("mainstruct", y, self.substruct)
        #12 + 64*16 = 1036 bytes long

        self.assertEqual(self.mainstruct.struct_len, 1036)

    def test_varlen_raw(self):
        x = (("integer", "INTUL"),
             ("varlen", "RAW/integer"))
        self.varlenstruct = Struct("varlenstruct", x)

        fp.seek(32 + 9 + 20 + 22, 0) #8, b"\x10\x20\x40\x80\x01\x02\x04\x08" in hex, 12 bytes in length
        #data = b"\x08\x00\x00\x00\x10\x20\x40\x80\x01\x02\x04\x08"

        self.assertEqual(self.varlenstruct.parse(fp),
                         {'integer': 8, 'varlen': b'\x10\x20\x40\x80\x01\x02\x04\x08'})

    def test_varlen_str(self):
        x = (("integer", "INTUL"),
             ("varlen", "STR/integer"),
             ("varlen2", "STR/integer"))
        self.varlenstruct = Struct("varlenstruct", x)

        fp.seek(32+9+20+22+12, 0) #data = b"\x04\x00\x00\x00\x54\x4d\x50\x54\x58\x54\x31\x32"
        #TMPTXT12 in hex, 12 bytes in length

        self.assertEqual(self.varlenstruct.parse(fp),
                        {'integer': 4,'varlen': 'TMPT','varlen2': 'XT12'})

    def test_parse_nul(self):
        x = (("integer", "INTUL"),
             ("short", "SHORTUL"),
             ("float", "FLOATUL"),
             ("long", "LONGUL"))
        self.nulstruct = Struct("nulstruct", x)
        
        fp.seek(32+9+20+22+12+12, 0)
        #18 bytes of nul, for each int type
        
        self.assertEqual(self.nulstruct.parse(fp),
                         {'integer':0, 'short':0, 'float':0, 'long':0})

    @unittest.expectedFailure
    def test_bad_kvs(self):
        x = (("bad type", "BAD", "BAD"),)
        self.badstruct = Struct("bad_struct", x)

        print("Main struct's len = %i" %self.badstruct.get_struct_len("mainstruct"))


if __name__ == "__main__":
    fp = open("test_data.bin", "rb")
    unittest.main()
    fp.close()


