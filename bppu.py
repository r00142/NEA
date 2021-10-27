from argparse import ArgumentParser
from core import BSPInterface, Backup
from config import Config
from pathlib import Path
from os import path
from time import time

argparser = ArgumentParser(description="Parse or pack a BSP file",
                                        epilog="-file, -dir, -fdlist, and -noauto will have no effect unless -pack is present",
                                        usage="%(prog)s [-h] path [-parse] [-pack] [-noauto] [-file FILE] [-dir DIRECTORY] [-fdlist FDLIST]")

argparser.add_argument("path", type=str,
                                   help="The path of the target BSP.")
argparser.add_argument("-parse", dest="parse", default=False, action="store_true",
                                   help="Parse the BSP and display information on files that would need to be packed, and files currently packed.")
argparser.add_argument("-pack", dest="pack", default=False, action="store_true",
                                   help="Pack files or directories into the BSP.")
##argparser.add_argument("-repack", dest="repack", default=False, action="store_true",
##                                   help="Repack the file after any files are packed.")

##packing arguments  
argparser.add_argument("-noauto", dest="noauto", default=False, action="store_true",
                                   help="Do not pack files scanned and found to be used but not in the BSP")                     
argparser.add_argument("-file", dest="file", action="append",
                                   help="Adds a file+path to pack.")
argparser.add_argument("-dir", dest="dir", action="append",
                                   help="Adds a directory to pack.")
argparser.add_argument("-fdlist", dest="fdlist", action="append",
                                   help="The path to a file that contains many files or directories to pack.")

args = argparser.parse_args()
config = Config()

bsp_path = args.path.strip("/\\")
    
try:
    bsp_path.relative_to(config.getkv("tf_path"))
except:
    bsp_path = Path(config.getkv("tf_path")) / bsp_path
if not(path.exists(bsp_path)):
    raise IOError("BSP %s not found" %bsp_path)


with open(bsp_path, "r+b") as fp:
    starttime = time()
    
    fdlist = []
    if args.pack and args.fdlist:
        fdlist = args.fdlist
    interface = BSPInterface(fp, fdlist)
    
    if args.parse:
        interface.list_needed_assets()
        parsetime = time()
        print("Parse finished in %s seconds" %round(parsetime-starttime, 2))
    else:
        parsetime = time()

    try:
        if args.pack:
            Backup.backup_file(fp.name)
            if not(args.noauto):
                interface.autopack_assets()
            if args.file:
                interface.pack_assets(args.file)
            if args.dir:
                interface.pack_assets(args.dir)
            packtime = time()
            print("Packing finished in %s seconds" %round(packtime-parsetime, 2))
        else:
            packtime = time()
                
    except Exception as error:
        Backup.restore_backup(fp.name)
        print("\nA fatal error occured during packing. Backups restored\n")
        raise (error) from None
        
