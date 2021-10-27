



## **Embedding arbitrary data within Binary Space Partition files**



*Implement sources, table of content, appendix w/ code into report*

*Reading school SharePoint - NEA guidance document*

*Remove objectives if they can't be met easily*

*Open shot for free video editing*

---

[TOC]




## Analysis:
####  *__Introduction__*
###### Background for the project, and related terminology
The BSP (Binary Space Partion) file format is a bespoke binary file format designed for the Source game engine. 
It is formed of distinct, structured pieces of data, known as 'lumps', each with their own unique format of storing their data and with a particular type of data that they store. 
At the file's beginning, a header table is implemented. This table table contains information for every lump - the offset from the start of the file, the length of the lump, the lump's version, and the lump's compressed size (if compressed). The table is prefixed by a constant + the BSP's version, and postfixed by the BSP's revision.
In the BSP file, all lumps are placed in a predefined order. The contents of these lumps ranges from data on 3D planes in the engine to lighting information (the result of complex radiosity equations and other lighting calculations), and there are always 64 lumps in a BSP file.
For those who use the Source engine to build 3D environments, they must embed any external assets not packaged with the engine into the final BSP file in a particular way - this is within a lump known as the 'pakfile' lump. The pakfile lump is a PKzip file archive located at the end of the BSP file, containing data on all external assets that an end user may require to correctly view the BSP file, and this is the lump that I focus on primarily.

My program's purpose is to both embed files within this pakfile lump, and to parse several other lumps in the file to obtain information on assets that should be packed by my program. My main goal is to improve on the functionality that existing tools try to implement yet fall short on in aspects.

![Example environment from the Source Engine](https://r00142.s-ul.eu/rhx4Mmd1)

*An example environment from the Source Engine. Much of the foliage that can be seen here is a custom asset, all of which will need to be included into the pakfile lump for end users to be able to see them*



#### *__Research__*

###### The BSP file format and its structure
Within the BSP file format, there are 64 defined lumps each with their own format. My program only has a particular interest in four of these lumps - lumps 0, 35, 40, and 43 - and the file's header. The following diagrams can be followed left to right, top to bottom and describe visually how each lump is structured.

BSP file header:

- The file header is a table containing, for every lump, the offsets from the file's beginning, its length, version, and uncompressed size (if compressed). It is also preceded by a constant of value VBSP and the file version, and followed by the file's revision. This header table is always 1036 bytes long.

- The structure is visually as follows, with each small box representing four bytes:

   ![Header table structure](https://r00142.s-ul.eu/nea-bak/cbyNzaX9)

BSP lump 0:
- Lump 0 is an ascii text buffer storing entity data for the file. It does not have a consistent defined format like every other lump, instead being formed of tens if not hundreds of many various substructures. Due to this lack of an easily parsable structure, I plan on linearly searching through the lump to obtain the information I need.

- An example of how part of lump 0 might look is as follows :

  ![Lump 0 format example](https://r00142.s-ul.eu/1p3OGr4C)

BSP lump 35:
- Lump 35 is a container lump, within which are several sub-lump structures known as 'gamelumps'. It firsts consists of a header made up of the number of gamelumps and an array of gamelump information similar to the BSP's file header. Each array entry contains the gamelump's ID defining what data it contains, its flags, version, offset, and length. 

- After this header, each gamelump follows along with the data they contain.

- The structure is visually as follows, with each box representing 4 bytes (flags and version are two-byte shorts):

  ![Lump 35 structure](https://r00142.s-ul.eu/0wINtw0Q)

BSP lump 40:
- Lump 40 is structured as a PKzip archive file, within which are multiple Local File Header structures containing file name, file data, and some additional file information, and File Header structures containing further information such as offsets to their respective Local File Header.
- At the end of the lump, an End of Central Directory structure exists to indicate how many file headers there are within the archive, as well as information on the 'central directory' - this is the collection of file headers that make up the body of the central . The naming is simply a remnant of the PKzip format's original use as a multiple-floppy-disc archive format.
- [Macro structure of lump 40 [7] :](#[7] - The structure of a PKzip file - https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip.html)!["Structure of a PKzip file"](https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-images/general-layout.png)

BSP lump 43:
- Lump 43 simply consists of concatenated 2D asset filepaths, each filepath being up to 128 bytes long and separated by hexadecimal NUL (00) symbols. In the BSP it usually acts as a table of stored data that is indexed into by other lumps, however in my program I only require the file paths themselves so I simply linearly parse this lump for all file paths contained.

  

###### Examples of existing systems
There are four main existing tools for this job:

- [Compilepal[1]](#[1] - Compilepal - https://compilepal.ruar.ai/) is an automated compiling utility for converting raw environment data files into BSP files, and includes a packing utility. This is currently the most popular tool but it has its downsides - the automated packing feature is generally very good but can miss files, and manual packing with this tool can be difficult and confusing; the packing utility can be confusing to use if not compiling the BSP with CompilePal; the GUI for the tool is not very clear as to what is being packed and what has not been packed, and will sometimes incorrectly report an unpacked file as being packed.
- [VIDE[2]](#[2] - VIDE - http://www.riintouge.com/VIDE/) is a multi-purpose tool for manipulating BSPs and other source engine asset files, and has an improved implementation of another tool known as PakRat. It is vastly superior to its predecessor however struggles with an unclear manual packing utility, an automatic utility that cannot detect certain file types or files in particular directories, and corruption of BSPs in some edge cases.
- [PakRat[3]](#[3] - PakRat - https://www.bagthorpe.org/bob/cofrdrbob/pakrat.html) is a GUI replacement for Source's built-in commandline packing utility bspzip.exe, and was at one point the main GUI packing utility for the Source Engine, but now struggles to function properly with newer Source Engine builds. VIDE contains an improved version of this tool.
- bspzip.exe, a commandline tool that ships with almost every Source game, contains many packing utilities for those who know how to use commandline tools, however newer users to the tool may struggle with knowing how to use it correctly, and it contains no way to easily view files within the BSP without extracting the files to desktop.

Additionally, my client has tried to use both VIDE and CompilePal, however both left them feeling unsatisfied - with VIDE they disliked manually packing custom content and how the autopack would miss some files, while with CompilePal they found that some files, particularly HUD files, would be missed by the tool; they then had to use CompilePal's manual packing tools, in which they had to individually add every single file they needed. They preferred CompilePal over VIDE due to how much easier it is to use than VIDE, but were still left wanting for improvements on their packing process.

I feel I'm able to combine the best of these programs - an automatic scanning utility that will not miss files or pack them multiple times; a manual file adding utility that can also draw a list of files to add from an external file; a packing tool that can identify files related to a single specified file to make manual packing faster for the user; and a clear, simple GUI that effectively communicates available options and what has/hasn't been packed.



###### End users

I've talked to a member of a community that creates environments using this engine and asked them for what they found problematic with the current tools, and potential features they'd like to see.

- "The thing about Vide that I don't like manually packing custom stuff, and the thing about compilePal that it doesn't compile everything I need, so misses some files like HUD icons or PD/CTF custom models. You have to manually include them" [HUD icons and custom models are various assets used by the engine]
- "It's good for compilePal to have this [manual packing] feature, but doing this I can't include bunch of files at once. Need to like, go through the whole process for each file + doing it not only for vtf, but for vmt too" [VTF and VMT files describe 2D assets for the engine, and each 2D asset has at least one VMT and VTF file associated. This means that with CompilePal, it can take a lot of time manually adding all custom files.]
- "Also feature I want that I think would be cool to have is used custom files list like, what custom assets are packed, from which folders and (if possible) who made by. I never bother to list all custom assets I use on the site, so I think it will be useful" [Custom assets are often sourced from external creators, and should be credited when used by someone]

We discussed potential goals for the program, and came up with three basic ones that they feel should be implemented:

- Auto-scan that checks all file references in the .BSP, to ensure that any file types used are packed into the file (current tools often miss certain types).
- Externally specified file that contains a list of assets that will be packed in if not added automatically by the scan.
- Listing files packed into the .BSP, as well as authors (if the authors are specified in an external file).


#### *__Software/hardware__*
###### Programming language choices
*Potential language choices:*

- Python would be my first choice for a language, particularly for the main bulk of the project, as I am familiar with this over other languages. A disadvantage of python is it is slightly slower than other languages so may not be suitable for algorithms that may take a longer time to execute.
- C/C++ is my secondary choice for this - their execution speeds for certain algorithms may be helpful, however they are more complicated than python and I have less experience
- YAML would be my choice if I was to need a structured language for any external files aside from config files, as it is simple and human readable - both my program and end users could edit this as needed
- INI files are my choice for external config files, as it is an easy to use file-type with a lot of existing documentation and libraries in languages that can read from and write to this.

My final choice is python for coding, as I am familiar with it and I feel it's generally fast enough to deal with the algorithms I'm implementing. I will also be using .ini files to store user configurations persistently, which will be application settings as well as directories to be read from.



###### Volumes of data
In general, the volumes of data I will work with will be between 5 and 100Mb. The size of some of these files may rend some algorithms slower (particularly the linear algorithms such as parsing structures, parsing lump 0's text, and LZMA compression) however the table of offsets in the header table and in lump 40 make parsing much quicker than it would be if I had to linearly parse the entire BSP file. I hope that my choice of python as a language will not negatively impact speed.



###### SMART objectives 

1. Automatic scanning of file references within the BSP. 
   - 1.1 - scan lump 0 linearly, searching for keywords to find referenced assets

   - 1.2 - parse lump 35 to obtain model filenames

   - 1.3 - parse lump 43 to obtain material filenames

   - 1.4 - collate list of referenced assets
2. External file containing a list of filepaths to external assets/a list of directories (FDlists) that the program will pack if not already present in the file. 
   - 2.1 - load external file if specified
   - 2.2 - parse file to obtain list of filenames
   - 2.3 - compare with automatic list and add any items that don't appear
3. Listing all files currently packed into the BSP, alongside additional information.
   - 3.1 - parse lump 40
   - 3.2 - display relevant fields, such as size in bytes and filenames
4. Adding and removing folders or files from within the tool.
   - 4.1 - packing lump 40 if supplied with a filename (or list of)
   - 4.2 - allow for addition of files from lump 40
   - 4.3 - automatically packing assets referenced in the BSP that exist
   - 4.4 -  check if a file is present in l40 before adding it to the BSP file
   - 4.5 - backup the BSP file, restoring the backup if an error occurs.
5. Implementing a config file.
   - 5.1 - store /tf/ path after retrieving from VProject environment variable
   - 5.2 - store a list of FDlist files to be automatically included
   - 5.3 - store a list of filenames to be ignored with every pack

<!--all finished as of 22/09/21-->


---

## Design:
#### ***System overview***
Based off of the objectives from my analysis section, I've split the program into several modular components. This allows for me to more easily modify each part of the program, test each individual component, and update code with new features. Thus, an overview of the program looks as follows where each different box is a separate file:![Main code functionality plan](https://r00142.s-ul.eu/CyEYLf73)

###### Structure library

A library I wrote to facilitate the easy reading and writing of structured binary data as I would be working with it so much. This library operates via 'struct' objects, each of which contains a set structure made up of many datatypes such as integers, chars, arrays of other datatypes, or an array of other structs. These objects then have the ability to read or write data from/to a file in the format specified by the structure. 

It contains several different datatypes to suit different types and forms that the data may take, and operates as unsigned little endian for the most part as the engine rarely if ever uses signed types, and only text is stored as big endian.

The datatypes implemented are as follows:

| Datatype        | Format                        | Purpose                                      |
| --------------- | :---------------------------- | -------------------------------------------- |
| Integer         | INTUL                         | Basic type                                   |
| Short           | SHORTUL                       | Basic type                                   |
| Long            | LONGUL                        | Basic type                                   |
| Float           | FLOATUL                       | Basic type                                   |
| Character       | CHARL                         | Basic type                                   |
| Constant        | \<constant>                   | Test if an expected value exists             |
| Variable length | <RAW/STR>/\<length>           | Read a given length of binary or text data   |
| Array           | \<datatype/struct>/\<repeats> | Repeat another datatype by \<repeats> amount |

Variable lengths, or varlens, are used primarily to read embedded file data or file names for use with my program. Arrays can contain repeats of any other datatype in addition to repeats of an external structure - this allows for the reading of more complex files with repeats of fixed structures.

Both varlens and arrays can take the value of an integer, long, or short as their value for length or repeats. This lets the parser dynamically read data that may vary in length when that length is given elsewhere in the file.

Additionally when packing binary varlens, the data can be given as 'PATH/\<filepath>'. This tells the structure parser to write data from a file to the given location in place of the filepath.

###### Header interface

The header interface parses the header at the start of the BSP file and can also return data for specific lump IDs, update the header table with new lengths or offsets for lumps, or return the entire header. It also validates whether the file is a BSP file or not, by checking the constant 'VBSP' that appears at the start of every BSP.

###### Lump parsers
There are four lump parsers in total, each parsing a different section of the BSP based on their defined formats - lumps 0, 35, 40, and 43. Each inherits from a base lump class allowing me to access the same interface for each lump, and the modularity lets me easily isolate parsers for testing or add/remove new parsers. Each can parse their respective lump and return relevant data (namely asset names or paths) formatted correctly to be used with the rest of the program.
###### Lump 40 packer
This packer is passed a list of filepaths, and will automatically calculate CRC32 values, offsets for file headers, lengths for each section of the pakfile lump, file length, and additional information for every file given. It will then then read each file's data and write everything in the correct format to the target BSP file and update the header table.

###### Config

This creates a config file with default values if none exists, or loads the config file if it does. The main purpose of this is to allow for users to change some parts of the program such as the Source Engine directory that assets are stored in, or FDlists to be included with every run of the tool. 

The config class acts as a simple wrapper of python's configparser library, and can easily return specified keyvalues for other parts of the program to use in addition to creating a default file, or write keyvalues if I implement a system for the program to automatically edit config files in the future.

###### File families

File families were created so that I could organise paths more easily such that I can consistently format groups of paths into a single format, and easily iterate through them to find all assets under a particular directory. As I work with many different files from various directories I've found them helpful to organise the smaller groups of files that often exist together such as those for material or model files; quickly check if a directory exists; and fetch every file with a particular type of filepath instead of having to iterate through every single asset to check.

###### MDL file

This class simply parses model files and returns 'skins' used by the file. While a model file contains the information for each vertex of the object, it internally references external material files that define how each vertex is coloured. 

###### Format assets

Many assets read from the BSP are not in a format that can be used directly as a filepath on the system - the format assets class will obtain the filenames of an actual asset on the disk from each asset, as well as any assets not included in the BSP but instead referenced in asset files such as model skins.

###### FDlists

FDlists are files containing a list of filenames to be manually included in a compile if they do not exist already. I've added this feature to help make manual file additions easier than CompilePal, and as such it also allows for only one file to be specified before the program will include all related files (e.g. specifying just a model file will get vertex data and material files for the model too).

###### Core

![Classes used in Core](https://r00142.s-ul.eu/0WXl2Fp3)

###### Command line interface
This allows for integration into existing tools such as CompilePal and for the writing of scripts that include the program. This will be the interface that end users interact with, and will display information about the file, its lumps, and files the user may wish to add.

#### ***Class diagram***

![Macro structure diagram](https://r00142.s-ul.eu/dnUEO2kR)

#### ***Algorithms used***
###### Structure parsing
![Structure parsing](https://r00142.s-ul.eu/nea-bak/FR2Wb5Rm)
The structure parsing algorithm loops through each data field in the struct object's defined structure, then parses data based on the datatype and returns an output dictionary with keys being each data field's name.

###### Structure packing
![Structure packing](https://r00142.s-ul.eu/Wby02QRQ)

The structure packing algorithm aims to insert packed data into a file at a given point however python cannot write into a file midway through. To overcome, this a temporary file is used within which data from the main file and given data is written in turn, before this temporary file overwrites the original file.

The packer assumes the passed in data is in the form of repeated blocks of data to be packed, thus it assumes the input array to contain blocks of data - each of which is an array or dictionary containing the data itself. Each block is then operated on, with the algorithm looping through the struct object's data fields and writing data from the block's respective fields into the file, formatted as their data fields specify. 

Additionally, an 'overwrite bytes' parameter allows for a certain amount of bytes to be overwritten by the parser to allow for modification of files as well as insertion.

###### Lump 0 parsing
![Lump 0 parsing](https://r00142.s-ul.eu/FCdhy4al)

Lump 0 does not follow the fixed format of every other lump, so I wrote a simple algorithm that searches for keyword-keyvalue pairs with specific keywords which attempts to fetch every keyvalue for defined keywords. This algorithm uses four key variables: 

- Buffer size - amount of data to read from the file each loop; 

- Lookback window size - how much to step back at the end of each buffer read to ensure a keyvalue is not missed if it is split by a buffer read's end; 

- Max read length - how much data should be read from each offset. As each keyvalue pair is in the format of "keyword" "keyvalue", this aims to capture the keyvalue from the data;

- Adjusted buffer size - this value determines how many buffer reads actually have to be performed to capture all data in the lump, and is also used to calculate each match index's offset to the lump's start (as they are originally given relative to each buffer read's start). It is buffer size-lookback window size

  

The algorithm reads buffer-size lengths of data, searching for every keyvalue in a predefined list, and appends offsets to an array. It then moves back lookback-window-size bytes to stop data from being missed at the end of the read, and repeats until no more buffers can be read. Max-read-length data is then read from each offset and the keyvalue split out, and an extension added.

Offsets are read instead of directly reading the data as I prefer to keep parts of my program modular, and it was easier to test knowing the offsets of data; however I may change this in the future so that data is directly read.

###### Lump 35 parsing

Initially, I parse the structure of lump 35 with the structure parser. In the 'SPRP' and 'DPRP' gamelumps, model names are stored in a list with each entry padded to 128 bytes. This allows me to simply compare the ID of each gamelump to see if it is one of the two I am interested in, then read the array of filenames before removing the padding from the start and end of each filename parsed.

###### Lump 40 parsing

###### Lump 40 packing

###### Lump 43 parsing

As lump 40 is an array of NUL-separated filenames, I parse the entire lump as a string then split on NUL-characters and add file extensions to any filenames without one already.

###### Formatting assets

This algorithm operates on an array of potential filenames. For each potential filename, it first determines if it is a specific type that needs to be operated on and acts accordingly.

Currently there are several filetypes that need to be modified so that I can locate the files that would actually be needed. Most if not all of these files are found by the Lump 0 Parser, so I add unique extensions to quickly identify which filenames must be modified. The modifications I have to make range from changing the path of potential assets to adding completely new potential assets with filenames based on the original potential asset's.

After modifying potential asset names, each one is checked to see if it is a valid asset path. File families are used here to speed up the process by eliminating directories that don't exist before their assets are scanned. I need to obtain only assets that exist, as these are the ones that the end user will need packed into their BSP file.

Each valid asset is then operated on - model file skins are obtained via my MDL parser, and model vertex files are added to the output array as well. Next, every VMT is opened and read to obtain any texture files or other VMT files referenced in the VMT but not in the BSP itself. This is done by searching for specific keywords and splitting out their keyvalues, and comparisons can be drawn to how the Lump 0 Parser operates.




#### ***Data volumes***

A BSP is generally between 5 and 80 megabytes from my experience - the size can vary wildly with the content stored within. Total assets used can take up only one or two megabytes, or up to several hundred in rare scenarios.

In my test data, made up of 5249 individual BSP files and mostly comprised of packed files, the mean filesize is 13.4 megabytes.

#### ***GUI***

The user interface of this program is implemented as a command line utility, created with python's argparser library. Only the path positional flag is required, being the location of the BSP to be operated on.
-parse will give data on the BSP, namely what files are referenced and what files need to be packed into the BSP.
-pack will pack files specified by -file, -dir, and -fdlist into the BSP.
-repack will apply LZMA compression to each lump of the BSP file.
-noauto will stop the program from auto-packing files referenced in the BSP, if the -pack flag is set.
The file, directory, and FDlist (file & directory list) commands can be used multiple times for however many items are needed to be packed - an FDlist is a text file containing, on each line, a file or directory to be packed into the BSP, which allows for reusing packed content lists or for auto-generating lists of many files that need to be packed.

I have chosen to use a command line interface so that the tool can be integrated into scripts and other programs, such as compilepal - it is also easier to design and implement than a full GUI program.

*GUI*:![GUI](https://r00142.s-ul.eu/nea-bak/daMpYNmY)

<!-- Add screenshots of parse and pack interface -->

---



## Implementation:
###### *Showcase key algorithms (write own when possible, e.g. hashing, matrix operations, sort algorithms) and key skills, as well as models used such as mathematical models, client server models, complex user defined use of OOP models*



---


## Testing:
###### *Test plan - see online notebook for this e.g. test number, objective, description, data/type, expected outcome, actual outcome*
###### *Ongoing testing - show as many as you need to show the most challenging parts*
###### *Final testing - video + screenshots showing the system working - test number, objective, description, data/type, expected outcome, actual outcome, evidence (screenshot/video link + timestamp)*
###### *Make a video of the working system including tests, it's a lot more efficient than taking many screenshots*

- Ensure the marker knows that each objective is fulfilled via testing.
- Show normal operation of the program as the user moves through it (e.g. using breakpoints to show data values).
- Each test should have its purpose, the test data used, the expected outcome, and the actual outcome all explained
- Instead of using unit tests, show that the right output data is being written and the file is valid.

---



## Evaluation:
###### *Capturing thoughts as I've moved through the project*

---

## Sources

###### *[1] - CompilePal - https://compilepal.ruar.ai/*

###### *[2] - VIDE - http://www.riintouge.com/VIDE/*

###### *[3] - PakRat - https://www.bagthorpe.org/bob/cofrdrbob/pakrat.html*

###### *[4] - public/zip_uncompressed.h - https://hg.alliedmods.net/hl2sdks/hl2sdk-bgt/annotate/80044e1b14cc/public/zip_uncompressed.h*

###### *[5] - HxD - https://mh-nexus.de/en/hxd/*

###### *[6] - GCFscape - https://nemstools.github.io/pages/GCFScape-Download.html*

###### *[7] - The structure of a PKzip file - https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip.html)*

---

## Technical Solution

- Ensure the solution meets all the requirements of the system (can show well through thorough testing).
- Signpost higher level technical skills demonstrated in code (e.g. written summary of each class naming functions where complex features are demonstrated).