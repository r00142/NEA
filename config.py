import configparser
import os
from pathlib import Path

class Config():
    def __init__(self):
        self.__cfile = "config.ini"
        self.__standardcfgs = ["tf_path"]
        self.__config = configparser.ConfigParser(allow_no_value = True)
        
        if not(os.path.exists(self.__cfile)):
            try:
                vproject = Path(os.environ["VProject"])
            except KeyError:
                raise ValueError("VProject dir environment variable does not exist")
            if not(os.path.exists(vproject / "tf2_misc_dir.vpk")):
                raise ValueError("VProject dir does not appear to be set to the /tf/ directory")
        
            self.__config.add_section("Core")
            self.__config.set("Core", ";TF path is set to the vproject dir by default. Change this to set it to somewhere else")
            self.__config.set("Core", "tf_path", str(vproject))
            self.__config.set("Core", ";If a file's extension is present here, it will not be listed when using -parse")
            self.__config.set("Core", "parse_ignore_ext", str([".vvd", ".vtx", ".phy"]))
            self.__config.set("Core", ";File Directory lists that are used for every file to be packed, if necessary")
            self.__config.set("Core", "permanent_fdlists", "[]")
            self.__config.set("Core", ";A list of files ignored by the auto-packer")
            self.__config.set("Core", "ignore", "[]")

            self.__writecf()
            
        else:
            pass
        

    def __writecf(self):
        with open(self.__cfile, "w") as cf:
                self.__config.write(cf)

    def __readcf(self):
        self.__config.read(self.__cfile)

    def getkv(self, kv):
        self.__readcf()
        return self.__config["Core"][kv]

##    def appendkv(self, kv, value):
##        r'''Exists for perma FDLists and IgnoreList, as they are treated as arrays of sorts
##        '''
##        self.__readcf()
##        if kv in self.__standardcfgs:
##            return
##        kvarr = list(self.__config["Core"][kv])
##        kvarr.append(value)
##        self.__config["Core"][kv] == str(kvarr)
##        self.__writecf()
##
##    def popkv(self, kv, value):
##        r'''Exists for perma FDLists and IgnoreList, as they are treated as arrays of sorts
##        '''
##        self.__readcf()
##        if kv in self.__standardcfgs:
##            return
##        kvarr = list(self.__config["Core"][kv])
##        kvarr.pop(value)
##        self.__config["Core"][kv] == str(kvarr)
##        self.__writecf()
