from .structure_parser import Struct, StructError
from .lump_class_base import LumpBaseParser, LumpBasePacker
from .header import HeaderParser, HeaderPacker
from zlib import crc32 as zcrc32
from pathlib import Path
import os

ZEOCDR = Struct("ZIP_EndOfCentralDirRecord",
        (("signature", "PK\x05\x06"), ## PK56
        ("numberOfThisDisk", "SHORTUL"),
        ("numberOfTheDiskWithStartOfCentralDirectory", "SHORTUL"),
        ("nCentralDirectoryEntries_ThisDisk", "SHORTUL"),
        ("nCentralDirectoryEntries_Total", "SHORTUL"),
        ("centralDirectorySize", "INTUL"),
        ("startOfCentralDirOffset", "INTUL"),
        ("commentLength", "SHORTUL"),
        ("comment", "STR/commentLength")))

#ZIP_FileHeader definition
ZFH = Struct("ZIP_FileHeader",
        (("signature", "PK\x01\x02"), ## PK12
        ("versionMadeBy", "SHORTUL"),
        ("versionNeededToExtract", "SHORTUL"),
        ("flags", "SHORTUL"),
        ("compressionMethod", "SHORTUL"),
        ("lastModifiedTime", "SHORTUL"),
        ("lastModifiedDate", "SHORTUL"),
        ("crc32", "INTUL"),
        ("compressedSize", "INTUL"),
        ("uncompressedSize", "INTUL"),
        ("fileNameLength", "SHORTUL"),
        ("extraFieldLength", "SHORTUL"),
        ("fileCommentLength", "SHORTUL"),
        ("diskNumberStart", "SHORTUL"),
        ("internalFileAttribs", "SHORTUL"),
        ("externalFileAttribs", "INTUL"),
        ("relativeOffsetOfLocalHeader", "INTUL"),
        ("fileName", "STR/fileNameLength"),
        ("extraField", "STR/extraFieldLength"),
        ("fileComment", "STR/fileCommentLength")))

#ZIP_LocalFileHeader definition
ZLFH = Struct("ZIP_LocalFileHeader",
        (("signature", "PK\x03\x04"), ## PK34
        ("versionNeededToExtract", "SHORTUL"),
        ("flags", "SHORTUL"),
        ("compressionMethod", "SHORTUL"),
        ("lastModifiedTime", "SHORTUL"),
        ("lastModifiedDate", "SHORTUL"),
        ("crc32", "INTUL"),
        ("compressedSize", "INTUL"),
        ("uncompressedSize", "INTUL"),
        ("fileNameLength", "SHORTUL"),
        ("extraFieldLength", "SHORTUL"),
        ("fileName", "STR/fileNameLength"),
        ("extraField", "RAW/extraFieldLength"),
        ("lfhData", "RAW/compressedSize")))

class FormatError(Exception):
    '''Error with formatted data
    '''
    pass

class Lump40Parser(LumpBaseParser):
    def __init__(self, fp, length=-1):
        r'''Pass a file object (with file pointer initialised to beginning of the lump) to this
        '''
        #dummy length for consistent interface
        super().__init__(fp, length)

    def parse(self): #returns an array of the contents
        headerparser = HeaderParser(self._fp)
        self._lump_offset = headerparser.get_single_lumpt(40)["fileofs"]
        
        l40_zeocdr_len = ZEOCDR.struct_len + 32 #zipendofcentraldir length plus comment (32 by default)
        self._fp.seek(-l40_zeocdr_len, 2)
        standard_offset = self._fp.tell()

        try:
            l40_zeocdr = ZEOCDR.parse(self._fp) #parsed zeocdr section of the file
        except StructError: #in case, for some odd reason, the zeocdr is padded (this has occured with a testing file)
            self._fp.seek(-75, 2)
            tdata = self._fp.read()
            self._fp.seek((-75+tdata.find(b"PK\x05\x06")), 2)
            temp_offset = self._fp.tell()
            l40_zeocdr = ZEOCDR.parse(self._fp)

            ##remove padding
            self._fp.seek(temp_offset-standard_offset, 2)
            try:            
                self._fp.truncate(self._fp.tell())
            except io.UnsupportedOperation:
                raise IOError("Set mode to r+ to enable writing - excess data requires trimming")
            
            
        l40_ncentraldirentries = l40_zeocdr["nCentralDirectoryEntries_Total"]
        l40_centraldiroffset = l40_zeocdr["startOfCentralDirOffset"]
        
        ## PARSING ZFH ##
        self._init_fp()

        self._fp.seek(l40_centraldiroffset, 1)
        
        l40_zfh = []
        
        for x in range(0, l40_ncentraldirentries):
            l40_zfh.append(ZFH.parse(self._fp))

        ## PARSING ZLFH ##
        l40_zlfh = []
        for x in l40_zfh:
            self._fp.seek(self._lump_offset+x["relativeOffsetOfLocalHeader"])
            l40_zlfh.append(ZLFH.parse(self._fp))

        output = {}
        output["zlfh"] = l40_zlfh
        output["zfh"] = l40_zfh
        output["zeocdr"] = l40_zeocdr
        return output
    

class Lump40Packer(LumpBasePacker):
    def __init__(self, fp):
        super().__init__(fp)

    def pack(self, ffmanager):
        r'''Data is assumed to be a file family manager pointing to all files to be packed
        ZFH, ZLFH, and ZEOCDR sections are formatted automatically
        '''
        
        l40parser = Lump40Parser(self._fp)
        l40data = l40parser.parse()
        headerparser = HeaderParser(self._fp)
        self._lump_offset = headerparser.get_single_lumpt(40)["fileofs"]


        self._fp.seek(-(ZEOCDR.struct_len+32), 2)
        zfh_offset = self._fp.tell()
        #zeocdr is last element of the file and preceded by the ZFH array
        
        zlfh_offset = self._lump_offset + l40data["zeocdr"]["startOfCentralDirOffset"]
        relative_zlfh_offset = l40data["zeocdr"]["startOfCentralDirOffset"]

        zfh_arr, zlfh_arr = [], []
        ncentraldirs, cumulativesize, lenincrease, cumulativefname = 0, 0, 0, 0
        for family in ffmanager.file_families:
            for asset in family.assets:
                path = family.path / asset
                ## ZFH ##
                ##offset to end of existing zfh array
                crc32, size, filename, fnamelen = 0, 0, None, 0
                ncentraldirs += 1
            
                filename = str(path)

                with open(ffmanager.parent_path / path, "rb") as fp:
                    while True:
                        chunk = fp.read(1 << 14)
                        if not chunk:
                            break
                        crc32 = zcrc32(chunk, crc32)
                ## see https://forum.allaboutcircuits.com/threads/crc32-calculation-under-windows.123698/#post-995625
                ## for validity checks of magic number \xde\xbb\x20\xe3, if necessary.

                size = os.path.getsize(ffmanager.parent_path / path)

                if "\\" in filename:
                    filename.replace("\\", "/")
                if not(Path(os.path.relpath(path, "custom")).parts[0] == ".."): #this was a nightmare to figure out
                    filename = str(path.relative_to(sorted(path.parents)[2]))
                    
                fnamelen = len(filename)
                
                
                zfh_arr.append({'signature': 'PK\x01\x02',
                                'versionMadeBy': 20,'versionNeededToExtract': 10,
                                'flags': 0, 'compressionMethod': 0,
                                'lastModifiedTime': 0, 'lastModifiedDate': 0,
                                'crc32': crc32,
                                'compressedSize': size, 'uncompressedSize': size,
                                'fileNameLength': fnamelen,
                                'extraFieldLength': 0,
                                'fileCommentLength': 0, 'diskNumberStart': 0,
                                'internalFileAttribs': 0, 'externalFileAttribs': 0,
                                'relativeOffsetOfLocalHeader': relative_zlfh_offset,
                                'fileName': filename,
                                'extraField': '', 'fileComment': ''})
                relative_zlfh_offset += ZLFH.struct_len + fnamelen + size

                ## ZLFH ##

                ##for compressed data (lzma), compressionMethod becomes \x0e\x00 only in the ZLFH
                zlfh_arr.append({"signature": "PK\x03\x04", "versionNeededToExtract": 10,
                                "flags": 0,
                                "compressionMethod": 0,
                                "lastModifiedTime": 0,
                                "lastModifiedDate": 0,
                                "crc32": crc32,
                                "compressedSize": size,
                                "uncompressedSize": size,
                                "fileNameLength": fnamelen,
                                "extraFieldLength": 0,
                                "fileName": filename,
                                "extraField": '',
                                "lfhData": "PATH/"+str(ffmanager.parent_path) + "\\/" + str(path)})

                cumulativesize += size
                cumulativefname += fnamelen
                lenincrease += (size + fnamelen*2 + ZLFH.struct_len + ZFH.struct_len)
                

        ##ZEOCDR
        new_zfh_offset = l40data["zeocdr"]["startOfCentralDirOffset"] + ncentraldirs*ZLFH.struct_len + cumulativesize + cumulativefname
        new_centraldir_size = l40data["zeocdr"]["centralDirectorySize"] + ncentraldirs*ZFH.struct_len + cumulativefname
        ncentraldirs_total = l40data["zeocdr"]["nCentralDirectoryEntries_Total"] + ncentraldirs
        zeocdr_dict = {"signature": "PK\x05\x06",
        "numberOfThisDisk": 0, "numberOfTheDiskWithStartOfCentralDirectory" : 0,
        "nCentralDirectoryEntries_ThisDisk" : ncentraldirs_total,
        "nCentralDirectoryEntries_Total" : ncentraldirs_total,
        "centralDirectorySize": new_centraldir_size,
        "startOfCentralDirOffset": new_zfh_offset,
        "commentLength": 32, "comment": b"\x58\x5a\x50\x31\x20\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"}

        self._init_fp() #start of lump
        self._fp.seek(l40data["zeocdr"]["startOfCentralDirOffset"], 1) #end of ZLFH array
        ZLFH.pack(self._fp, zlfh_arr)
        self._fp.seek(l40data["zeocdr"]["centralDirectorySize"], 1) #end of ZFH array
        ZFH.pack(self._fp, zfh_arr)
        ZEOCDR.pack(self._fp, [zeocdr_dict,], overwrite_bytes = ZEOCDR.struct_len + 32)

        
        headerpacker = HeaderPacker(self._fp)
        headerdata = headerparser.parse() #modify this then write back afterwards
        headerdata["lump_t"][40]["filelen"] += lenincrease
        headerpacker.pack(headerdata)

    



