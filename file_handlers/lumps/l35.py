from .structure_parser import *
from .lump_class_base import LumpBaseParser

class Lump35Parser(LumpBaseParser):
    def __init__(self, fp, length=-1):
        super().__init__(fp, length)

        self.__DGL = Struct("dgamelump",
                        (("id", "STR/4"),
                         ("flags", "SHORTUL"),
                         ("version", "SHORTUL"),
                         ("fileofs", "INTUL"),
                         ("filelen", "INTUL")))
        self.__DGLH = Struct("dgamelumpheader",
                        (("lumpCount", "INTUL"),
                         ("dgamelump_t", "dgamelump/lumpCount")),
                        self.__DGL)
        self.__modelentry = Struct("modelentry",
                        (("name", "RAW/128"),))
        self.__modeldata = Struct("modeldata",
                        (("dictEntries", "INTUL"),
                         ("modelNames", "modelentry/dictEntries")),
                        self.__modelentry)
        

    def parse(self):
        self._init_fp()
        dglh = self.__DGLH.parse(self._fp)
        model_array = {}
        for x in dglh["dgamelump_t"]: #for each sublump
            self._fp.seek(x["fileofs"], 0)
            if x["id"] in ("prps", "prpd"):
                data = self.__modeldata.parse(self._fp)["modelNames"]
                modelnames = set(map((lambda data: data["name"].replace(b"\x00", b"")),
                                         data))
                model_array[x["id"]] = modelnames
            else:
##                model_array [x["id"]] = self._fp.read(x["filelen"])
                pass

        dglh["data_array"] = model_array
        
        return dglh
