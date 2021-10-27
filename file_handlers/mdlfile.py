from .lumps.structure_parser import Struct
from pathlib import Path


class MDLparser():
    def __init__(self, filepath):
        self.__MDLheader = Struct("mdl_file",
                            (("id", "IDST"),
                             ("version", "INTUL"),
                             ("checksum", "INTUL"), #should be same as in vtx and phy
                             ("name", "STR/64"),
                             ("dataLength", "INTUL"),
                             ("filler1", "RAW/72"), #data not needed
                             ("flags", "INTUL"),
                             ("filler2", "RAW/48"), #more data not needed
                             ("texture_count", "INTUL"), ("texture_offset", "INTUL"), #material filenames here
                             ("texturedir_count", "INTUL"), ("texturedir_offset", "INTUL"),
                             ("skinreference_count", "INTUL"), ("skinrfamily_count", "INTUL"),
                             ("skinreference_index", "INTUL"),
                             ("filler3", "RAW/216"))) #until end of struct (I do not need this data either)
                            ##408 bytes long

        self.__MDLmaterial = Struct("mdl_material",
                                     (("name_offset", "INTUL"), #num bytes past this structure's beginning to the name
                                      ("flags", "INTUL"),
                                      ("used", "INTUL"),
                                      ("unused", "INTUL"),
                                      ("material", "INTUL"),
                                      ("client_material", "INTUL"),
                                      ("unused2", "RAW/40")))
                                ##64 bytes long
        self.__MDLmaterial_final = Struct("mdl_material_fin",
                                              (("mdl_material", "mdl_material/1"),
                                              ("final_offset", "INTUL")),
                                              self.__MDLmaterial)

        self.__filepath = filepath

    def get_materials(self):
        with open(self.__filepath, "rb") as fp:
            data = self.__MDLheader.parse(fp)
            fp.seek(data["texture_offset"])
            offset_arr = []

            counter = 0
            for repeat in range(data["texture_count"]-1):
                counter += 1
                offset_arr.append(data["texture_offset"] + self.__MDLmaterial.parse(fp)["name_offset"] + 64*repeat)
            final_item = self.__MDLmaterial_final.parse(fp)
            offset_arr.append(data["texture_offset"] + final_item["mdl_material"][0]["name_offset"] + 64*counter)
            offset_arr.append(final_item["final_offset"])

            output_fnames = []
            fp.seek(final_item["final_offset"])
            path = "materials\\" + fp.read(data["dataLength"] - final_item["final_offset"] - 1).decode().strip("\x00")
            for x in range(len(offset_arr)-1):       
                fp.seek(offset_arr[x])
                output_fnames.append(path + fp.read(offset_arr[x+1]-offset_arr[x]-1).decode() + ".vmt")

            return list(map(Path, output_fnames))
