import unittest
##from lumps.header import *
from lumps.structure_parser import *


class TestStructs(unittest.TestCase):
    StructMaster = Struct()
    def test_basic01(self):
        x = (("int", "INT", "UL"),
             ("short", "SHORT", "UL"),
             ("long", "LONG", "SL"))
        self.StructMaster.new_struct("substruct01", x)
        self.assertEqual(self.StructMaster.get_struct_dict()["substruct01"], x)

    def test_substruct(self):
        x = (("int", "INT", "UL"),
             ("short", "SHORT", "UL"),
             ("long", "LONG", "SL"))
        self.StructMaster.new_struct("substruct02", x)
        
        y = (("int", "INT", "UL"),
             ("array", "substruct02/2", "SUB"))
        self.StructMaster.new_struct("mainstruct01", y)
        
        data = b"\x16\x00\x00\x00\x08\x00\x08\x00\x12\x01\x10\x00\x00\x00\x00\x00\x00\x00\x09\x00\x08\x00\x13\x01\x11\x00\x00\x00\x00\x00\x00\x00"
        # data = 22 524296 274 16 524297 275 17 in hex
        self.assertEqual(self.StructMaster.parse(data, "mainstruct01"),
                         {'int': 22, 'substruct02': [{'int': 524296, 'short': 274, 'long': 16},
                                                                      {'int': 524297, 'short': 275, 'long': 17}]})

    def test_const(self):
        x = (("constant", "CONST/TMP", "CN"),
             ("int", "INT", "UL"),
             ("short", "SHORT", "UL"))
        self.StructMaster.new_struct("conststruct01", x)
        data = b"\x54\x4d\x50\x01\x00\x00\x00\x02\x00" # TMP12 in hex
        self.assertEqual(self.StructMaster.parse(data, "conststruct01"),
                         {'constant': 'TMP', 'int': 1, 'short': 2})
        
    def test_arr(self):
        x = (("int", "INT", "UL"),
             ("array", "SHORT/8", "ARR"))
        self.StructMaster.new_struct("arrstruct01", x)
        data = b"\x08\x00\x00\x00\x12\x02\x22\x10\x75\x83\x13\x01\x22\x00\x20\x86\x92\x02\x53\x02"
        # 8 530 4130 33653 275 34 34336 658 595 in hex
        self.assertEqual(self.StructMaster.parse(data, "arrstruct01"),
                         {'int': 8, 'array': [530, 4130, 33653, 275, 34, 34336, 658, 595]})

    def test_parse_basic(self): #all basic types
        x = (("int", "INT", "UL"),
             ("short", "SHORT", "UL"),
             ("char", "CHAR", "UL"),
             ("float", "FLOAT", "UL"),
             ("long", "LONG", "UL"),
             ("const", "CONST/TMP", "CN"))
        self.StructMaster.new_struct("allstruct01", x)
        
        data = b"\x20\x01\x00\x00\x32\x00\x37\x00\x00\x41\x18\x18\x00\x00\x00\x00\x00\x00\x00\x54\x4d\x50"
        # 288 50 7 9.5 17 TMP in hex
        self.assertEqual(self.StructMaster.parse(data, "allstruct01"),
                                                            {'int': 288, 'short': 50, 'char': '7',
                                                            'float': 9.5, 'long': 24, 'const': 'TMP'})
    def test_get_len(self):
        x = (("fileofs", "INT", "UL"),
                    ("filelen", "INT", "UL"),
                    ("version", "INT", "UL"),
                    ("fourCC", "CHAR/4", "ARR"))
        self.StructMaster.new_struct("substruct03", x)
        #16 bytes long

        y = (("ident", "CONST/VBSP", "CN"),
                    ("version", "INT", "UL"),
                    ("lump_t", "substruct03/64", "SUB"),
                    ("revision", "INT", "UL"))
        self.StructMaster.new_struct("mainstruct02", y)
        #12 + 64*16 = 1036 bytes long

        self.assertEqual(self.StructMaster.get_len("mainstruct02"), 1036)

    def test_varlen_raw(self):
        x = (("integer", "INT", "UL"),
             ("varlen", "RAW/integer", "VAR"))
        self.StructMaster.new_struct("varlenstruct01", x)

        data = b"\x08\x00\x00\x00\x10\x20\x40\x80\x01\x02\x04\x08"
        #260, b"\x10\x20\x40\x80\x01\x02\x04\x08" in hex

        self.assertEqual(self.StructMaster.parse(data, "varlenstruct01"),
                         {'integer': 8, 'varlen': b'\x10\x20\x40\x80\x01\x02\x04\x08'})

    def test_varlen_str(self):
        x = (("integer", "INT", "UL"),
             ("varlen", "STR/integer", "VAR"),
             ("varlen2", "STR/integer", "VAR"))
        self.StructMaster.new_struct("varlenstruct02", x)

        data = b"\x04\x00\x00\x00\x54\x4d\x50\x54\x58\x54\x31\x32"
        #TMPTXT12 in hex

        self.assertEqual(self.StructMaster.parse(data, "varlenstruct02"),
                        {'integer': 4,'varlen': 'TMPT','varlen2': 'XT12'})
    

if __name__ == "__main__":
    unittest.main()



##
##z = (("bad type", "BAD", "BAD"),)
##StructMaster.new_struct("bad_struct", z)
##
##print("Main struct's len = %i" %StructMaster.get_struct_len("mainstruct"))
##
##bsp = "l40_testing\\lump40_format_testing.bsp"
##with open(bsp, "rb", 1036) as bsp_file:
##    bsp_header = bsp_file.read(1036)
##
##x = header.parse(bsp_header)
##print('\n'.join('{}: {}'.format(*k) for k in enumerate(x)))
