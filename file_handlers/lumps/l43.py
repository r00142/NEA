from .structure_parser import Struct
from .lump_class_base import LumpBaseParser

class Lump43Parser(LumpBaseParser):
    def __init__(self, fp, length=-1):
        super().__init__(fp, length)
        #texdata string data
        self.__TSD = Struct("TexdataStringData",
                    (("TexdataStringData", "RAW/"+str(self._lump_len)),))

    def __fixup_path(self, filepath):
        if filepath[-4:] in [b".VMT", b".vmt"]:
            return "MATERIALS/" + filepath.decode()
        return "MATERIALS/" + filepath.decode() + ".VMT"
        
    def parse(self):
        self._init_fp()
        output_str = self.__TSD.parse(self._fp)
        output = output_str["TexdataStringData"].split(b"\x00")

        if not(output[-1]): output.pop() #removes last element if None
        
        output = list(map(self.__fixup_path, output))
        return output
