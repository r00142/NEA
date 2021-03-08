from header import HeaderParser
from structure_parser import *


class L40Parser():
    def __init__(self, bsp_path):
        self.__HeaderMaster = HeaderParser(bsp_path)
        self.__headerdata = self.__HeaderMaster.get_header_data()
        
        self.__l40_offset = self.__headerdata["header"]["lumps"][40]["fileofs"]
        self.__l40_len = self.__headerdata["header"]["lumps"][40]["filelen"]
        del self.__HeaderMaster # no further use for this HeaderParser object
        
        with open(bsp_path, "rb") as bsp_file:
            self.__l40_data = bsp_file.read()
            self.__l40_data = self.__l40_data[self.__l40_offset:self.__l40_offset+self.__l40_len]

        

        #### Creating structures - ZIP_EndOfCentralDirRecord, ZIP_FileHeader, ZIP_LocalFileHeader
        self.__StructMaster = Struct()
        #ZIP_EndOfCentralDirRecord definition
        self.__ZEOCDR = (("signature", "CONST/PK\x05\x06", "CN"), ## PK56
                ("numberOfThisDisk", "SHORT", "UL"),
                ("numberOfTheDiskWithStartOfCentralDirectory", "SHORT", "UL"),
                ("nCentralDirectoryEntries_ThisDisk", "SHORT", "UL"),
                ("nCentralDirectoryEntries_Total", "SHORT", "UL"),
                ("centralDirectorySize", "INT", "UL"),
                ("startOfCentralDirOffset", "INT", "UL"),
                ("commentLength", "SHORT", "UL"),
                ("comment", "STR/commentLength", "VAR"))

        #ZIP_FileHeader definition
        self.__ZFH = (("signature", "CONST/PK\x01\x02", "CN"), ## PK12
               ("versionMadeBy", "SHORT", "UL"),
               ("versionNeededToExtract", "SHORT", "UL"),
               ("flags", "SHORT", "UL"),
               ("compressionMethod", "SHORT", "UL"),
               ("lastModifiedTime", "SHORT", "UL"),
               ("lastModifiedDate", "SHORT", "UL"),
               ("crc32", "INT", "UL"),
               ("compressedSize", "INT", "UL"),
               ("uncompressedSize", "INT", "UL"),
               ("fileNameLength", "SHORT", "UL"),
               ("extraFieldLength", "SHORT", "UL"),
               ("fileCommentLength", "SHORT", "UL"),
               ("diskNumberStart", "SHORT", "UL"),
               ("internalFileAttribs", "SHORT", "UL"),
               ("externalFileAttribs", "INT", "UL"),
               ("relativeOffsetOfLocalHeader", "INT", "UL"),
               ("fileName", "STR/fileNameLength", "VAR"),
               ("extraField", "STR/extraFieldLength", "VAR"),
               ("fileComment", "STR/fileCommentLength", "VAR"))

        #ZIP_LocalFileHeader definition
        self.__ZLFH = (("signature", "CONST/PK\x03\x04", "CN"), ## PK34
               ("versionNeededToExtract", "SHORT", "UL"),
               ("flags", "SHORT", "UL"),
               ("compressionMethod", "SHORT", "UL"),
               ("lastModifiedTime", "SHORT", "UL"),
               ("lastModifiedDate", "SHORT", "UL"),
               ("crc32", "INT", "UL"),
               ("compressedSize", "INT", "UL"),
               ("uncompressedSize", "INT", "UL"),
               ("fileNameLength", "SHORT", "UL"),
               ("extraFieldLength", "SHORT", "UL"),
               ("fileName", "STR/fileNameLength", "VAR"),
               ("extraField", "STR/extraFieldLength", "VAR"))


        self.__StructMaster.new_struct("ZIP_EndOfCentralDirRecord", self.__ZEOCDR)
        self.__StructMaster.new_struct("ZIP_FileHeader", self.__ZFH)
        self.__StructMaster.new_struct("ZIP_LocalFileHeader", self.__ZLFH)





    def parse_l40_getcontents(self): #returns an array of the contents
        l40_data_copy = self.__l40_data
        l40_zeocdr_len = self.__StructMaster.getlen("ZIP_EndOfCentralDirRecord")+32 #plus comment len
        output = []
        
        ## PARSING THE ZEOCDR ##
        l40_zeocdr = self.__StructMaster.parse(l40_data_copy[-l40_zeocdr_len:],
                                                   "ZIP_EndOfCentralDirRecord")#zfh array begins at "startOfCentralDirOffset" from the lump's start
        offset = 0

        l40_ncentraldirentries = l40_zeocdr["ZIP_EndOfCentralDirRecord"]["nCentralDirectoryEntries_Total"]
        l40_centraldiroffset = l40_zeocdr["ZIP_EndOfCentralDirRecord"]["startOfCentralDirOffset"]

        ## PARSING THE ZFH ARRAY ##
        for x in range(0,l40_ncentraldirentries ):
            zfh = self.__StructMaster.parse(l40_data_copy[
                                int(l40_centraldiroffset)+offset : -l40_zeocdr_len],
                                "ZIP_FileHeader")
            output.append(zfh)

            zfh_fnlen = zfh["ZIP_FileHeader"]["fileNameLength"] #filename length
            zfh_eflen = zfh["ZIP_FileHeader"]["extraFieldLength"] #extra field len
            zfh_fclen = zfh["ZIP_FileHeader"]["fileCommentLength"] #file comment len
            zfh_size = self.__StructMaster.getlen("ZIP_FileHeader") + zfh_fnlen + zfh_eflen + zfh_fclen

            offset += zfh_size
            
        return output

            
    def parse_l40_getzip(self): #writes all contents to a zip file
        try:
            zip_fname = "root.zip"
            with open(zip_fname, "xb") as zip_file:
                zip_file.write(self.__l40_data)
            print("packed data written to %s" %zip_fname)
        except FileExistsError as e:
            raise FileExistsError(e) #pass error to whatever is calling this higher up


    def pack_l40_singlefile(filepath):
        pass


if __name__ == "__main__":
    bsp_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf\\maps\\lump40_format_testing.bsp"
    Lump40Parser = L40Parser(bsp_path)
    for x in Lump40Parser.parse_l40_getcontents():
        print(x["ZIP_FileHeader"]["fileName"])

        

    ## Lump40Parser.parse_l40_getzip()



