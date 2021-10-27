from copy import deepcopy
from pathlib import Path

class FileFamily():
    def __init__(self):
        r'''A file family collects multiple asset names sharing the same path.
        '''
        self.path = b""
        self.assets = []

    def set_path(self, path):
        self.path = path

    def add_asset(self, fname):
        if fname not in self.assets:
            self.assets.append(fname)

    def remove_asset(self, fname):
        try:
            self.assets.remove(fname)
            return 1
        except:
            return 0

class FileFamilyManager():
    def __init__(self, data, parent_path=None):
        r'''A file family manager initialises and manages a group of file families.
        Pass in a list of Path objects and a parent Path object
        A parent path is a shared path of all file families if there is one
        '''
        self.file_families = []
        self.parent_path = parent_path

        template = FileFamily()

        for path in data:
            try:
                item = Path(path).relative_to(self.parent_path) #everything after parent path  
            except:
                item = Path(path)
            is_path = False
            for ff in self.file_families:
                if item.parent == ff.path:
                    ff.add_asset(item.name)
                    is_path = True
            if not is_path:
                ffobj = deepcopy(template)
                ffobj.set_path(item.parent)
                ffobj.add_asset(item.name)
                self.file_families.append(ffobj)

    def get_num_assets(self):
        numassets = 0
        for family in self.file_families:
            for asset in family.assets:
                numassets += 1
        return numassets

    def remove_asset(self, fpath):
        try:
            item = fpath.relative_to(self.parent_path)
        except:
            item = fpath

        for ff in self.file_families:
            if item.parents[0] == ff.path:
                ff.remove_asset(item.name)
