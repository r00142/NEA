from header import HeaderParser
from structure_parser import *


class L40Parser():
    def __init__(self, bsp):
        self.__HeaderMaster = HeaderParser(bsp)
        self.__headerdata = self.__HeaderMaster.get_header_data()
        
        self.__l40_offset =self.__headerdata["header"]["lumps"][40]["fileofs"]
        self.__l40_len = self.__headerdata["header"]["lumps"][40]["filelen"]
        with open(bsp, "rb") as bsp_file:
            self.__l40_data = bsp_file.read()
            self.__l40_data = self.__l40_data[self.__l40_offset:self.__l40_offset+self.__l40_len]

        

        #### Creating structures - ZIP_EndOfCentralDirRecord, ZIP_FileHeader, ZIP_LocalFileHeader
        self.__StructMaster = Struct()
        #ZIP_EndOfCentralDirRecord
        self.__ZEOCDR = (("signature", "CONST/PK\x05\x06", "CN"), ## PK56
                  ("numberOfThisDisk", "SHORT", "UL"),
                  ("numberOfTheDiskWithStartOfCentralDirectory", "SHORT", "UL"),
                  ("nCentralDirectoryEntries_ThisDisk", "SHORT", "UL"),
                  ("nCentralDirectoryEntries_Total", "SHORT", "UL"),
                  ("centralDirectorySize", "INT", "UL"),
                  ("startOfCentralDirOffset", "INT", "UL"),
                  ("commentLength", "SHORT", "UL"))
                ## comment follows

        #ZIP_FileHeader
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
               ("relativeOffsetOfLocalHeader", "INT", "UL"))
                ## folloewd by file name, extra field, and file comment - all variable field len

        #ZIP_LocalFileHeader
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
               ("extraFieldLength", "SHORT", "UL"))
                ## followed by file name, extra field - all variable field len

        self.__StructMaster.new_struct("ZIP_EndOfCentralDirRecord", self.__ZEOCDR)
        self.__StructMaster.new_struct("ZIP_FileHeader", self.__ZFH)
        self.__StructMaster.new_struct("ZIP_LocalFileHeader", self.__ZLFH)

        ## print(self.__StructMaster.parse(self.__l40_data, "ZIP_LocalFileHeader"))

    def parse_l40_getcontents(self): #returns an array of the contents
        l40_data_copy = self.__l40_data
        output = []

        while True:
            if l40_data_copy[:4] == b"PK\x03\x04": #zip local file header
                l40_parsed = self.__StructMaster.parse(l40_data_copy, "ZIP_LocalFileHeader") #parsed to allow easy indexing
                fcompr_len = l40_parsed["ZIP_LocalFileHeader"]["compressedSize"] #compressed file contents len
                fname_len = l40_parsed["ZIP_LocalFileHeader"]["fileNameLength"] #filename len
                efield_len = l40_parsed["ZIP_LocalFileHeader"]["extraFieldLength"] #extra field len
                l40_data_copy = l40_data_copy[self.__StructMaster.getlen("ZIP_LocalFileHeader"):]
                
                fname = l40_data_copy[:fname_len].decode() #filename
                efield = l40_data_copy[fname_len:fname_len+efield_len].decode() #extra field
                l40_data_copy = l40_data_copy[fname_len+efield_len+fcompr_len:] #amending data used

                print("file %s found in BSP" %(fname))
                output.append({"filename":fname, "extra field":efield, "size":fcompr_len})
                
            else:
                print("non-ZLFH struct found, magic number was instead %s" %l40_data_copy[:4])
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
    Lump40Parser.parse_l40_getcontents()
    ## Lump40Parser.parse_l40_getzip()



