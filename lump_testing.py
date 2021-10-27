##from file_handlers.file_family import FileFamily, FileFamilyManager
from core import BSPInterface# , backup_file, restore_backup
from file_handlers.lumps.header import HeaderParser

from file_handlers.format_assets import FormatAssets
from file_handlers.mdlfile import MDLparser
from core import ParseLumps


##from lumps.l0 import Lump0Parser
##from lumps.l35 import Lump35Parser
from file_handlers.lumps.l40 import Lump40Parser, Lump40Packer
##from lumps.l43 import Lump43Parser
import os
from pathlib import Path
import time


##bsp_path = "file_handlers\\lumps\\l40_testing\\cp_zinkenite_b3a.bsp"
##bsp_path = "file_handlers\\lumps\\l40_testing\\pl_upward.bsp"
##bsp_path = "file_handlers\\lumps\\l40_testing\\ctf_2fort_uncompressed.bsp"
##bsp_path = "file_handlers\\lumps\\l40_testing\\gypsum_blend.bsp"
bsp_path = "file_handlers\\lumps\\l40_testing\\lump40_format_testing.bsp"
if not(os.path.exists(bsp_path)):
    raise IOError("BSP %s not found" %bsp_path)
bsp_path = Path(bsp_path)

##mdlfile = MDLparser(Path("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf\\models\\crowbar\\cars\\musclecar001.mdl"))
##
##print(mdlfile.get_materials())

with bsp_path.open("r+b") as fp:
    assets_interface = BSPInterface(fp, "test_fdlist.fdl")
##    starttime = time.time()

##    assets_interface.list_needed_assets()
####    print(Format.get_needed_assets())
##    assets_interface.autopack_assets()

    
##    print(time.time()-starttime)




    
##main program rough setup
##print(final_assets)
##this all works somehow
##final output is all referenced unique assets + those referenced in VMTs

###next, pack the assets into l40. wipe the lump and construct new zeocdrs/etc





##l0
##fp = open(bsp_path, "rb")
##HeaderMaster = HeaderParser(fp)
##headerdata = HeaderMaster.parse()
##l0_offset = headerdata["lump_t"][0]["fileofs"]
##l0_len = headerdata["lump_t"][0]["filelen"]
##
##fp.seek(l0_offset)
##Lump0Parser = Lump0Parser(fp, l0_len)
##print(Lump0Parser.parse())
##
##
##fp.close()

##l35
##fp = open(bsp_path, "rb")
##HeaderMaster = HeaderParser(fp)
##headerdata = HeaderMaster.parse()
##l35_offset = headerdata["lump_t"][35]["fileofs"]
##l35_len = headerdata["lump_t"][35]["filelen"]
##
##fp.seek(l35_offset)
##Lump35Parser = Lump35Parser(fp)
##
##parsed_data = Lump35Parser.parse()
##
##print(parsed_data)
##print("gamelump header table entries:")
##for x in parsed_data["dgamelump_t"]:
##    print("Gamelump %s information:\n\tflags: %i, version: %i, offset: %i, length: %i"%(x["id"], x["flags"], x["version"], x["fileofs"], x["filelen"]))
##
##for y in parsed_data["data_array"]:
##    print("%s: \n%s" %(y, parsed_data["data_array"][y]))
##
##fp.close()

##l40
##with open(bsp_path, "rb") as fp:
##    HeaderMaster = HeaderParser(fp)
##    headerdata = HeaderMaster.parse()
##    l40_offset = headerdata["lump_t"][40]["fileofs"]
##    l40_len = headerdata["lump_t"][40]["filelen"]
##    fp.seek(l40_offset)
##    Lump40Parse = Lump40Parser(fp)
##    data = Lump40Parse.parse()
##
##
##
##bsp_path = "lumps\\l40_testing\\test_tmp.bsp"
##
##with open(bsp_path, "r+b") as fp2:
##    fp2.write(b"\x05\x06\x05\x06")
##    fp2.seek(0)
##    Lump40Packer = Lump40Packer(fp2)
##    Lump40Packer.pack(data)



##l43
##fp = open(bsp_path, "rb")
##HeaderMaster = HeaderParser(fp)
##headerdata = HeaderMaster.parse()
##l43_offset = headerdata["lump_t"][43]["fileofs"]
##l43_len = headerdata["lump_t"][43]["filelen"]
##
##fp.seek(l43_offset)
##Lump43Parser = Lump43Parser(fp, l43_len)
##output = Lump43Parser.parse()
##print(output)
        
##x = FileFamilyManager(output)
##for y in x.file_families:
##    print(y.path)
##    for item in y.assets:
##        print("- %s" %item)


####################
## VPK structure is echoed in the file families format, as a tree
## Material [ directory [ filename ] ] ]
## Format in file is (type)NUL(dir)NUL(filename)NUL(18 bytes)
## Any number of dirs and filenames can exist under a type
####################

##vpk = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf\\tf2_misc_dir.vpk"
##
##fp2 = open(vpk, "rb")
##vpkdat = fp2.read()

##for x in range(len(output)-1, -1, -1):
##    if vpkdat.find(bytes(output[x].split("/")[-1], "utf-8")) != -1:
##        print("asset %s found in VPKs" %output[x])

##print("Referenced textures:")
##for x in output:
##    print("  -  %s" %x)

##fp.close()
