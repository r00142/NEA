from .structure_parser import Struct
from .lump_class_base import LumpBaseParser
import re
import time

class Lump0Parser(LumpBaseParser):
    def __init__(self, fp, length):
        super().__init__(fp, length)

        self.__BUFFER_SIZE = 4096
        self.__LOOKBACK_WINDOW_SIZE = 48 #looks back so that strings are captured if split at the end of the buffer
        self.__MAX_READ_LEN = 96 #how many bytes to read looking for each item's material/etc, larger values slow the search but potentially catch longer names

        if self._lump_len < (self.__BUFFER_SIZE-self.__LOOKBACK_WINDOW_SIZE):
            self.__BUFFER_SIZE = self._lump_len
            

        #based on the default fgd for tf2
        self.__search_once = [b'"skyname"', b'"detailvbsp"', b'"detailmaterial"'] #all string searched for only once
        self.__search_repeats = [b'"material"', b'"model"\x20"models', b'"overlaymaterial"',
                                 b'"RopeMaterial"', b'"team_model"', b'"team_icon"', b'"PlayVO"',
                                 b'"flag_icon"', b'"flag_paper"', b'"flag_trail"', b'"powerup_model"',
                                 b'"pickup_model"', b'"pickup_particle"', b'"point_warn_sound"',
                                 b'"icon"', b'"hud_icon"', b'"res_file"', b'"hud_res_file"',
                                 b'"ParticleEffect"', b'"gibmodel"', b'"filename"', b'"effect_name"'] #all strings searched multiple times for
        self.__so_extensions = [b".IS_SKY", None, b".vmt"]
        self.__sr_extensions = [b".vmt", None, b".vmt",
                                None, None, b".vmt", None,
                                b"_*.vmt", b".IN_PCF", b"_*.vmt", None, #Note that particles will be contained in PCFs..
                                None, None, b".IN_SOUND_SCRIPT",
                                b".vmt", None, None, None,
                                b".IN_PCF", None, None, b".IN_PCF"]
        
        
    def __init_parse_fp(self):
        self._fp.seek(-self.__LOOKBACK_WINDOW_SIZE, 1)

    def __fixup_array(self, string):
        index = string.find(b'"\x20"') + 3 #splits each item in the lump
        index2 = string.find(b'"', index)
        if index2 == -1:
            raise IndexError("issue parsing lump 0; max read len")
        return string[index:index2]

    def parse(self):    
        self._init_fp()
        ##Basic algorithm for searching##
        index_dict, extension_list = [], []
        item_offset = 0
        ADJUSTED_BUFFER_SIZE = self.__BUFFER_SIZE-self.__LOOKBACK_WINDOW_SIZE #accounts for the lookback window used to ensure no missed matches
        buffer_read_amount = self._lump_len//ADJUSTED_BUFFER_SIZE #how many buffer reads to loop through
        if self._lump_len%self.__BUFFER_SIZE:
            buffer_read_amount += 1

        
        for buffer_read in range(0, buffer_read_amount):
            file_data = self._fp.read(self.__BUFFER_SIZE)
            self.__init_parse_fp()
            
            for item in self.__search_once:
                extension_index = self.__search_once.index(item)
                item_offset = file_data.find(item)
                if item_offset != -1: #if it appears
                    index_dict.append(item_offset + buffer_read*(ADJUSTED_BUFFER_SIZE))
                    extension_list.append(self.__so_extensions[extension_index])
                    
            for item in self.__search_repeats:
                extension_index = self.__search_repeats.index(item)
                item_offset = 0
                while item_offset != -1:
                    item_offset = file_data.find(item, item_offset+len(item))
                    if item_offset != -1:
                        index_dict.append(item_offset+buffer_read*(ADJUSTED_BUFFER_SIZE))
                        extension_list.append(self.__sr_extensions[extension_index])

        items_array = []
        for x in index_dict:
            self._init_fp()
            self._fp.seek(self._lump_offset + x)
            items_array.append(self._fp.read(self.__MAX_READ_LEN))

        output = map(self.__fixup_array, items_array)
        output = map((lambda string, extension : (string+extension) if extension else string),
                         output, extension_list)
            

        return set(output) #eliminate duplicates with set()
