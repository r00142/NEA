from file_handlers.file_family import FileFamilyManager
from file_handlers.format_assets import FormatAssets
from file_handlers.fdlist import FDlist
from file_handlers.lumps.header import HeaderParser
from file_handlers.lumps.l0 import Lump0Parser
from file_handlers.lumps.l35 import Lump35Parser
from file_handlers.lumps.l40 import Lump40Parser, Lump40Packer
from file_handlers.lumps.l43 import Lump43Parser
from config import Config
from pathlib import Path
import shutil
import os

class ParseLumps():
    def __init__(self, fp):
        self.__l0_ofs = None
        self.__l35_ofs = None
        self.__l35_len = None
        self.__l40_ofs = None
        self.__l43_ofs = None
        self.__l43_len = None
        
        self.__fp = fp
        self.__origoffset = self.__fp.tell()
        
        parser = HeaderParser(self.__fp)
        self.__l0_ofs = parser.get_single_lumpt(0)["fileofs"]
        self.__l0_len = parser.get_single_lumpt(0)["filelen"]
        self.__l35_ofs = parser.get_single_lumpt(35)["fileofs"]
        self.__l40_ofs = parser.get_single_lumpt(40)["fileofs"]
        self.__l43_ofs = parser.get_single_lumpt(43)["fileofs"]
        self.__l43_len = parser.get_single_lumpt(43)["filelen"]
        del parser
        self.__init_fp()

    def __init_fp(self):
        self.__fp.seek(self.__origoffset)

    def __parse(self, offset, parser, length = None):
        self.__fp.seek(offset)
        
        parser = parser(self.__fp, length)
        self.__init_fp()
        return parser.parse()

    def parse_lump(self, lumpno):
        if lumpno == 0:
            self.__init_fp()
            return self.__parse(self.__l0_ofs, Lump0Parser, self.__l0_len)
        elif lumpno == 35:
            self.__init_fp()
            return self.__parse(self.__l35_ofs, Lump35Parser)
        elif lumpno == 40:
            self.__init_fp()
            return self.__parse(self.__l40_ofs, Lump40Parser)
        elif lumpno == 43:
            self.__init_fp()
            return self.__parse(self.__l43_ofs, Lump43Parser, self.l43_len)
        else:
            self.__init_fp()
            return ["Lump %s parsing not implemented" %lumpno]

    def __force_lower(self, data):
        try:
            return data.decode().lower()
        except:
            return data.lower()
    
    def get_assets(self):
        output = []

        output += self.__parse(self.__l0_ofs, Lump0Parser, self.__l0_len)

        l35_data = self.__parse(self.__l35_ofs, Lump35Parser)["data_array"]
        for gamelump in l35_data:
            output += l35_data[gamelump]

        output += self.__parse(self.__l43_ofs, Lump43Parser, self.__l43_len)

        self.__init_fp()
        return set(map(self.__force_lower, output))


class BSPInterface():
    def __init__(self, fp, fdlists):
        self.__cfg = Config()
        self.__TF_PATH = Path(self.__cfg.getkv("tf_path"))
        self.__fp = fp
        self.__Parse = ParseLumps(self.__fp)

        permfdlists = self.__cfg.getkv("permanent_fdlists")
        if permfdlists != "[]":
            fdlists = list(fdlists) + list(self.__cfg.getkv("permanent_fdlists"))
        if fdlists:
            for item in fdlists:
                item = Path(item)
        self.__FDlist = FDlist(fdlists)
        
        fixed_paths = []
        for path in self.__FDlist.get_list():
            if (self.__TF_PATH / path).is_dir():
                for asset_path in list((self.__TF_PATH / path).glob("**/*")):
                    fixed_paths.append(asset_path.relative_to(self.__TF_PATH))
            else:
                fixed_paths.append(path)
        
        self.__Format = FormatAssets(set(list(self.__Parse.get_assets()) + fixed_paths), self.__TF_PATH)

    def list_all_assets(self):
        assets = self.__Format.get_all_assets()
        
        print("Assets used:")
        for path in assets.file_families:
            print("\%s:" %path.path)
            for asset in path.assets:
                print(" - %s" %asset)

    def __fixup_size(self, size):
        if size < 1024**2:
            return "%sKB" % round(size/1024, 2)
        elif size >= 1024**2 and size < 1024**4:
            return "%sMB" % round(size/(1024**2), 2)
        else:
            return "%sGB" % round(size/(1024**4), 2)


    def list_needed_assets(self):
        assets = FileFamilyManager(self.__Format.get_needed_assets(), self.__TF_PATH)
        totalcount, totalsize, l40fcount = 0, 0, 0
        l40data = self.__Parse.parse_lump(40)
        existingassets = []
        
        for item in l40data["zlfh"].copy(): #for cubemaps in the pakfile lump
            if item["fileName"][:3] == "sp_" and item["fileName"][-4:] == ".vhv":
                l40data["zlfh"].remove(item)

        for family in assets.file_families:       
            if Path(os.path.relpath(family.path, "custom")).parts[0] != "..":
                for item in l40data["zlfh"]:
                    existingassets.append(Path("custom") / family.path.parts[1] / item["fileName"])
                    
        for item in l40data["zlfh"]:
            l40fcount += 1
            existingassets.append(Path(item["fileName"]))

        print("Used assets found in /tf/ folder and FDlists:")
        for path in assets.file_families:
            print("%s\\" %path.path)
            for asset in path.assets:
                if asset[:3] == "sp_" and Path(asset).suffix == ".vtf":
                    pass
                elif Path(asset).suffix in self.__cfg.getkv("parse_ignore_ext"):
                    totalcount += 1
                else:
                    size = os.path.getsize(self.__TF_PATH / path.path / asset)

                    if path.path / asset not in existingassets:
                        prefix = "+++"
                    else:
                        prefix = "---"
                    print("\t%s %s | size: %s" %(prefix, asset, self.__fixup_size(size)))
                        
                    totalcount += 1
                totalsize += os.path.getsize(self.__TF_PATH / path.path / asset)

        print("\nTotal size of %i individual files is %s" %(totalcount, self.__fixup_size(totalsize)))

        ignorepaths_arr = self.__cfg.getkv("parse_ignore_ext").strip("[]").replace("'", "").replace(" ", "").split(",")

        for item in range(len(ignorepaths_arr)-1):
            print("%s, " %ignorepaths_arr[item], end="")
        print("and %s files were not listed\n" %ignorepaths_arr[-1])            



    def autopack_assets(self):
        assets = self.__Format.get_needed_assets()
        print("Assets retrieved..")
        
        removedcount = 0
        for asset in assets:
            if str(asset.relative_to(self.__TF_PATH)) in self.__cfg.getkv("ignore"):
                assets.remove(asset)
                removedcount += 1

        if removedcount:
            print("Ignored %i assets while packing a file.. modify config if this was unintentional" %removedcount)
        self.pack_assets(assets)
            
    def pack_assets(self, filepaths):
        l40packer = Lump40Packer(self.__fp)
        hparser = HeaderParser(self.__fp)
    
        
        files = FileFamilyManager(filepaths, self.__TF_PATH)

        l40data = self.__Parse.parse_lump(40)
        l40fcount= 0
        for item in l40data["zlfh"].copy():
            if item["fileName"][:3] == "sp_" and item["fileName"][-4:] == ".vhv":
                l40data["zlfh"].remove(item)

        for family in files.file_families:
            if Path(os.path.relpath(family.path, "custom")).parts[0] != "..":
                for item in l40data["zlfh"]:
                    if not files.remove_asset(Path("custom") / family.path.parts[1] /
                                                   item["fileName"]):
                        files.remove_asset(Path("custom") / family.path.parts[1] /
                                                item["fileName"].lower())

                
        for item in l40data["zlfh"]:
            l40fcount += 1
            if not files.remove_asset(Path(item["fileName"])):
                files.remove_asset(Path(item["fileName"].lower()))

        if l40fcount > 0:
            print("%i files already present in pakfile lump.. ignored these if attempting to pack them again" %l40fcount)

        if files.get_num_assets() == 0:
            print("No assets need packing..")
            return
        
        try: #pack
            self.__fp.seek(hparser.get_single_lumpt(40)["fileofs"])
            l40packer.pack(files)
            print("%i assets packed successfully .." %files.get_num_assets())

        except Exception as error: #except an error occured while packing
            raise error from None

    def remove_assets(self, filepaths):
        pass

class Backup():
    @staticmethod           
    def backup_file(filepath):
        path = Path(filepath)
        r'''Creates a backup of the file referenced with path.
        Path should include file name and extension in addition to the filepath.
        '''
        extension = path.suffix
        shutil.copy(path, path.with_suffix(extension+".backup")) #backing up the file

    @staticmethod
    def restore_backup(filepath):
        r'''Restores the file referenced with path from the backup of filepath
        '''
        path = Path(filepath)
        extension = path.suffix
        if os.path.exists(path.with_suffix(extension+".backup")):
            shutil.copy(path.with_suffix(extension+".backup"), path)
        else:
            raise IOError("No file with the name %s exists" %path.with_suffix(extension+".backup"))
