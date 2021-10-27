import os
from .file_family import FileFamilyManager
from .mdlfile import MDLparser
from pathlib import Path



class FormatAssets():
    def __init__(self, asset_paths, tf_path):
        r'''pass in an array of relative path objects and the /tf/ folder absolute path
        '''
        self.__TF_PATH = tf_path
        paths_arr, fixed_paths = [], []
        for path in asset_paths:
            paths_arr.append(self.__TF_PATH / path)

        
        for path in paths_arr:
            ## - team materials - ## 
            ## fix this up later ##
            if "*" in str(path):
                fixed_paths.append(Path(str(path).replace("*", "red"))) ## look into pathlib glob
                fixed_paths.append(Path(str(path).replace("*", "blu"))) ## to try and find relevant files
                fixed_paths.append(Path(str(path).replace("*", "neutral"))) ## instead of assuming it is always these three
            ## - skies - ##
            elif path.suffix == ".is_sky":
                parent = path.parent
                end = path.stem
                for side in ["bk", "dn", "ft", "lf", "rt", "up"]:
                    fixed_paths.append(parent / "materials\skybox" / (end+side+".vmt"))
                    fixed_paths.append(parent / "materials\skybox" / (end+"_hdr"+side+".vmt"))
                    #hdr may not be in the BSP but included anyway
            ## - particles - ##
            elif path.suffix == ".in_pcf":
                pass ##update me
            ## - sound scripts - ##
            elif path.suffix == ".in_sound_script":
                pass ##update me
            ## - cubemaps/wvt patches - ##
            elif path.is_relative_to(self.__TF_PATH / "materials\maps"):
                asset = path.name
                parent = path.parents[3] / path.parent.relative_to(path.parents[1])
                if "_wvt_patch" in asset:
                    fixed_paths.append(parent / asset.replace("_wvt_patch", ""))
                else:
                    index = asset.rfind("_", 0, asset.rfind("_", 0, asset.rfind("_"))) #format is matname_*_*_* so this removes unwanted info
                    index2 = asset.find(".")
                    if index == -1:
                        raise ValueError("Issue with cleaning cubemap materials")
                    fixed_paths.append(parent / (asset[:index] + asset[index2:]))
            elif path.suffix == "":
                raise ValueError("Path %s has no suffix" %path.relative_to(self.__TF_PATH))
            else:
                fixed_paths.append(path)


        self.__asset_families = FileFamilyManager(fixed_paths, self.__TF_PATH)


        self.__unique_assets = []
        for family in self.__asset_families.file_families: #standard paths
            if os.path.exists(self.__TF_PATH / family.path):
                for asset in family.assets: 
                    if os.path.exists(self.__TF_PATH / family.path / asset):
                        self.__unique_assets.append(self.__TF_PATH / family.path / asset)
        for folder in (folder for folder in (self.__TF_PATH / "custom").iterdir() if folder.is_dir()):
            for family in self.__asset_families.file_families:
            ##all subdirectories in /tf/custom
                for asset in family.assets:
                    if os.path.exists(folder / family.path / asset):
                        self.__unique_assets.append(folder / family.path / asset)

        ##fixup VMTs and MDLs properly
        output_assets = []
        search_assets = [(b"$fallbackmaterial", ".vmt"), (b"$bumpmap", ".vtf"),
                         (b"$normalmap", ".vtf"), (b"$bottommaterial", ""),
                         (b"%tooltexture", ".vtf"), (b"$basetexture", ".vtf")]
        max_read_len = 96
        offset = 0
        
        ## collect referenced/alike assets here
        for path in self.__unique_assets:
            ## - models - ##
            if path.suffix == ".mdl":
                for item in [".vvd", ".sw.vtx", ".dx80.vtx", ".dx90.vtx"]:
                    output_assets.append(path.parent / (path.stem + item))
                if os.path.exists(path.parent / (path.stem + ".phy")):
                    output_assets.append(path.parent / (path.stem + ".phy"))

                mdlfile = MDLparser(self.__TF_PATH / path)
                if Path(os.path.relpath(path, self.__TF_PATH / "custom")).parts[0] != "..":
                    #this was a nightmare to figure out
                    #the statement essentially figures out if it is a /custom/ folder or not
                    custompath = self.__TF_PATH / "custom" / (path.relative_to(self.__TF_PATH).parts[1])
                    materials = [(custompath / apath) for apath in mdlfile.get_materials().copy()]
                else:
                    materials = map(lambda path : self.__TF_PATH / path, mdlfile.get_materials().copy())
                    
                self.__unique_assets += materials
                del mdlfile
                
        for fpath in self.__unique_assets:
            #two separate loops so we can add materials from models
            ## - vmt references - ##
            if fpath.suffix == ".vmt" and os.path.exists(fpath):
                with open(fpath, "rb") as fp:
                    ##simplified version of lump 0 parsing, as files are far smaller
                    data = fp.read()
                    for item in search_assets:
                        offset = data.lower().find(item[0])
                        if offset != -1:
                            fp.seek(offset)
                            string = fp.read(max_read_len).decode().split("\n")[0].encode()
                            if data.lower().find(b"\"%s\"" %item[0]) == -1:
                                index1 = len(item[0]) + 2 
                            else:
                                index1 = len(item[0]) + 3 #sometimes the tag has "" around it, sometimes not
                                ##todo - look at different ways people might format VMTs
                                ##to allow for parsing materials from them even if weirdly formatted

                            index2 = string.find(b'"', index1)
                            
                            if Path(os.path.relpath(fpath, self.__TF_PATH / "custom")).parts[0] != "..":
                                #this was a nightmare to figure out
                                #the statement essentially figures out if it is a /custom/ folder or not
                                custompath = self.__TF_PATH / "custom" / (fpath.relative_to(self.__TF_PATH).parts[1])
                                asset = (custompath / "materials\\" / (string[index1:index2].decode() + item[1]))

                            else:
                                asset = (self.__TF_PATH / "materials\\" /
                                        (string[index1:index2].decode() + item[1]))
                                
                            if os.path.exists(asset):
                                output_assets.append(asset)

            if os.path.exists(fpath):
                output_assets.append(fpath)
            self.__unique_assets = output_assets

    def get_needed_assets(self):
        return self.__unique_assets

    
