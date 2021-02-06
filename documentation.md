

## **Embedding arbitrary files within Binary Space Partition files**

### *EXTRAS TODO* 

- [ ] Structure library
  - [x] Structure definitions and miscellaneous operations
  - [x] Parsing
  - [ ] Packing
- [x] Lump 40 parsing
- [ ] Lump 40 packing

### *SPECIAL SECTION: FILE FORMAT  BREAKDOWN AND IDENTIFYING HOW TO IMPLEMENT AN ALGORITHM FOR LUMP 40*

The BSP file format's lump 40 is interesting - a little official documentation exists, but it only seems to be in the form of offhand comments on the structure, as well as a list + the content of data structures present in it. This section is specifically being created to document my process of figuring out how the lump should be parsed.

#### *__The information supplied, tools used, and test data used for this process__*

From the official documentation, what we know is that lump 40 will contain files embedded into the .BSP; that lump 40 is structured identically to an uncompressed zip file; that [*public/zip_uncompressed.h[6]*](#[6] - public/zip_uncompressed.h - https://hg.alliedmods.net/hl2sdks/hl2sdk-bgt/annotate/80044e1b14cc/public/zip_uncompressed.h) defines the structures present, with ZIP_EndOfCentralDirRecord being the final structure in the lump that points to an array of ZIP_FileHeader structures, one for each file followed by the file's contents immediately after.

[*HxD[7]*](#[7] - HxD - https://mh-nexus.de/en/hxd/) will be used to view the raw hex data of the .BSP file, with another tool known as [*GCFscape[8]*](#[8] - GCFscape - https://nemstools.github.io/pages/GCFScape-Download.html) used to explore the file format and verify that the files have been embedded correctly when writing a tool to embed files.

The data I'll be using to test this will be a .BSP file I've created, with three files embedded within - a HUD .res file, used for additional user interface information; a .VMT and .VTF file describing a material asset present in the format; a simple .TXT file for content control - ensuring any format will work fine in this. I'll also be creating an empty version of this .BSP file, to test manually embedding the files later on. 

*The original packed BSP as seen in VIDE and GCFscape*![""](https://r00142.s-ul.eu/nea-bak/rZYzZMFj)

#### *_Parsing the lump_*

Looking at the file and using my structure parsing library, I could see that there's a constant identifying which structure it is (PK12, PK34, or PK56) at the start of each block - within this, there are fields describing various fields, among which are the file name, extra fields, comments, and data lengths if they exist in the structure. 

Once I implemented a variable length data type into my structure parser, I was able to read these fields and write them to external files. I was planning on also adding an option to set a field's length to that of another field, but I decided it would be too difficult to work with internally (with length calculation, as well as )

*Data present in the first zip local file header structure in the lump - the data piece's length is whatever the value of compressedSize is*![""](https://r00142.s-ul.eu/nea-bak/nwMvqRjo)

Next, using this data and the file I had, I started to implement two basic functions - one which would return a list of the file contents of lump 40, and one which would copy the entire lump to an external zip file (as the formats are nearly identical with no compression). The former was quite simple and just involved a While loop going through until until the ZIP_EndOfCentralDirRecord is encountered (signalling the end of the lump structure).  The latter simply wrote the entire contents of the lump to a zip file.

A more permanent solution will be implemented later for this, as I dislike how it breaks out of the while loop upon encountering a non-localfileheader object; I currently have no use for the ZIP_FileHeader objects (they simply contain a list of the file names present in the lump and references to their locations), nor the ZIP_EOCDR object present at the file's end. I'll likely need to use these when constructing my own lump 40s for packing, however that will be detailed later in this chapter.

*Methods for returning an array of all items present in the lump, and for extracting all contents to a zip file.*![""](https://r00142.s-ul.eu/nea-bak/Duw1r886)



---

Note:

*Implement sources, table of content, appendix w/ code into report*

*Reading school SharePoint - NEA guidance document*

*Remove objectives if they can't be met easily*

*Nuance naturally speaking 13 speech to text tool*

*Open shot for free video editing*

---

[TOC]




## Analysis:
<!--implement a gantt chart at some point in this section-->

####  *__Introduction__*
###### *What is the challenge to overcome? - setting the scene for the project*
This project is focusing on a utility for the Source engine, a game engine from the early 2000s with a still-active modding and game community. The utility will specifically pack files into the engine's Binary Space Partition map files, a task that modern tools still often struggle with. I feel building my own system for it will allow for adding in additional features into the tool that may not be present in other existing tools, as well as being able to improve current features.



#### *__Client__* 
###### *Regarding emails/meetings; documenting them, preparing questions and documenting answers; performing analysis*
Client specified objectives:

- Auto-scan that checks all file references in the .BSP, to ensure that HUD files and other miscellaneous data is packed in.
- Externally specified file that contains a list of assets that will be manually packed if not added automatically by the scan.
- Listing files packed into the .BSP, as well as authors (if specified in an external file.



#### *__Research__*
###### *Examples of existing systems; what's the functionality of them, what can be improved on, what is missing? - Surveys, books, media online (state sources)*
There are four main existing tools for this job:

- [Compilepal[1]](#[1] - Compilepal - https://compilepal.ruar.ai/), an automated compiling utility for converting unplayable level files into raw game-usable data, includes a packing utility. This is currently the most popular tool but it has its downsides - the automated packing feature is very good, however manual packing with this tool is often difficult and confusing; the packing utility can be confusing to use if not compiling the map with CompilePal; the GUI for the tool is not very clear as to what is being packed and what has not been packed, and will sometimes incorrectly report an unpacked file as being packed.
- [VIDE[2]](#[2] - VIDE - http://www.riintouge.com/VIDE/), a multi-purpose tool for manipulating BSPs and other source engine asset files, has an improved implementation of another tool known as PakRat. It is vastly better than its predecessor however struggles with an unclear manual packing utility, an automatic utility that often misses non-standard files, and corruption of BSPs if some steps are incorrectly followed.
- [PakRat[3]](#[3] - PakRat - https://www.bagthorpe.org/bob/cofrdrbob/pakrat.html), a GUI replacement for Source's built-in commandline packing utility bspzip.exe, it was once the best option for packing maps for most people but now struggles to function properly with newer source engine builds. VIDE contains an improved version of this tool.
- bspzip.exe, a commandline tool that ships with almost every source game, contains many packing utilities for those who know how to use commandline tools, however newer users to the tool may struggle with knowing how to use it correctly, and it contains no way to easily view files within the BSP without extracting the files to desktop.

Additionally, my client has tried to use both VIDE and CompilePal, however both left them feeling unsatisfied - with VIDE they disliked manually packing custom content, while with CompilePal they found that some files, particularly HUD files, would be missed by the tool; they then ran into the issue CompilePal's lacklustre manual packing tools, having to add every single file they used manually. They preferred CompilePal over VIDE due to how much easier it is to use that VIDE. 

I feel I'm able to combine the best of these programs - an automatic scanning utility that will not miss files or pack them multiple times; a manual file adding utility that can also draw a list of files to add from an external file; and a clear, simple GUI that effectively communicates available options and what has/hasn't been packed.




#### *__Software/hardware requirements__*
###### *identifying 3 languages; justifying the final choice - what coding method and approach will be used?*
###### Potential language choices:
- Python would be my first choice for a language, especially for the GUI, as I am familiar with this over other languages. A disadvantage of python is it is slower than other languages so may not be suitable for time-sensitive algorithms.
- C/C++ is my secondary choice for this - they are fast languages that I am fairly familiar with, however they are more complicated than python and I have less experience
- YAML would be my choice if I was to use a structured language for any external files aside from config files, as it is simple and human readable - both my program and end users could edit this as needed
- INI files are my choice for external config files, as it is an easy to use file-type with a lot of existing documentation and libraries in languages that can read from and write to this.

My final choice is python for coding, as I am familiar with it and I feel it's generally fast enough to deal with the algorithms I'm implementing. I will also be using .ini files to store user configurations persistently, which will be their settings as well as directories to be read from.



###### *Discussion with client/summarising system objectives - SMART objectives (specific, measurable, achievable, realistic, time-bound)*
###### *Prototyping - code algorithms/pseudocode/charts/diagrams; something suitable for your app*

[*Main code functionality plan[4]*](#[4] - Main code functionality plan - https://r00142.s-ul.eu/nea-bak/GVQ6YFl8):![Main program's functionality plan](https://r00142.s-ul.eu/nea-bak/GVQ6YFl8)

[*Overall code functionality plan[5]*](#[5] - Overall code functionality plan - https://r00142.s-ul.eu/nea-bak/eStLKnHg):![Overall program plan](https://r00142.s-ul.eu/nea-bak/eStLKnHg)

Lempel-Ziv-Markov chain algorithm implementation plan[6]: (not finished)

[*Structure parser parsing plan[9]*](#[9] -Structure parser parsing plan - https://r00142.s-ul.eu/nea-bak/tbFiB42H):![Structure parser parsing plan](https://r00142.s-ul.eu/nea-bak/tbFiB42H)



## Design:
#### ***System overview***
#### ***Class diagram***
#### ***Database - SQL statements, ERD, normalisation***   
#### ***Data dictionary - methods/attributes***
#### ***Data volumes***
#### ***GUI***
#### ***Security*** 

---



## Implementation:
###### *Showcase key algorithms (write own when possible, e.g. hashing, matrix operations, sort algorithms) and key skills, as well as models used such as mathematical models, client server models, complex user defined use of OOP models*

Early on when creating this program, I realised that I needed a better method of parsing structures that appeared in lumps. At first I manually created dictionaries as seen in the code insert below, however this was very inefficient, inelegant, and I could easily make mistakes by splicing the wrong portion of the file. I decided to create a system, not dissimilar to the existing python struct library, that will allow me to easily define structures for lumps to parse and write them.

```python
## inefficient old code used to define the header structure. ##
## btoi_ul converts unsigned little-endian bytearrays into integers ##
self.lumpt_array = []
for x in range(8, 1032, 16):
    self.lumpt_array.append(
        {"fileofs" : shared.btoi_ul(self.bsp_header[x : x+4]),
        "filelen" : shared.btoi_ul(self.bsp_header[x+4 : x+8]),
        "version" : shared.btoi_ul(self.bsp_header[x+8 : x+12]),
        "fourCC" : [shared.btoi_ul(self.bsp_header[x+12 : x+13]),
                    shared.btoi_ul(self.bsp_header[x+13 : x+14]),
                    shared.btoi_ul(self.bsp_header[x+14 : x+15]),
                    shared.btoi_ul(self.bsp_header[x+15 : x+16])]})

self.dheader_t = {"ident": self.bsp_header[:4],
                  "version": shared.btoi_ul(self.bsp_header[4:8]),
                  "lump_t": self.lumpt_array,
                  "mapRevision": shared.btoi_ul(self.bsp_header[1032:])}
```

My first implementation of this system used a slightly messy setup where an enum was used to switch between datatypes alongside list splicing to read datatypes/etc. An excerpt from just the length calculation code shows where the difficulties came in - from trying to crush both the datatype and unsigned/signed + little/big endian into the same field, and my poor implementation of sub-structures.

```python
lumps = Struct((
                ("fileofs", "INTUL"),
                ("filelen", "INTUL"),
                ("version", "INTUL"),
                ("fourCC", "fourCC[4]")))
## example structure that would work with this system

def __lencalc(self):
    for dtype in self.__struct: ## 2d tuple containing structure
        try:
            self.__structlen += Datatype[dtype[1][:3]].value
            ## messy list splicing method that's unnecessary - Datatype is an enum containing the datatype's sizes (in C) 
        except:
            try:
                self.__structlen += int(dtype[1].split("[")[1][:-1]) * getattr(eval(dtype[1].split("[")[0]), "getlen")()   
                ## extremely hard to read code relying on a lot of list splicing and the eval() method (a bad python practice)
            except:
                raise ValueError("Array value not correctly formatted - please give a valid struct object and follow the format <structure>[<amount>]")

```

When planning my updated code, I was following a few basic ideas:

- Three fields: NAME, TYPE, FLAGS (SIGNED/UNSIGNED + LITTLE/BIG) - this will cut down on unnecessary list splicing
- Structs are now not class objects, but dictionaries stored within a master object. this will bypass the need for eval on substructs.
- instead, getattr can be used for it instead - a lot easier than using the messy eval method
- More readable data names - since FLAGS are separated from TYPE, I can use the full names such as FLOAT instead of FLT, and CONST instead of CST.

With this new system, I can also do away with the messy try, except statements and if statements as I can indicate more easily if it's a substruct datatype or not.



\## TALK ABOUT NEW IMPLEMENTATION ##

This new method works far better. I still have to work out some minor issues, such as some values seemingly having three or four added to them, however it is easy to use and easier to maintain than the original solution.



---




## Testing:
###### *Test plan - see online notebook for this e.g. test number, objective, description, data/type, expected outcome, actual outcome*
###### *Ongoing testing - show as many as you need to show the most challenging parts*
###### *Final testing - video + screenshots showing the system working - test number, objective, description, data/type, expected outcome, actual outcome, evidence (screenshot/video link + timestam*p)
###### *Make a video of the working system including tests, it's a lot more efficient than taking many screenshots*

---



## Evaluation:
###### *Capturing thoughts as I've moved through the project*

## Glossary

###### *[1] - CompilePal - https://compilepal.ruar.ai/*

###### *[2] - VIDE - http://www.riintouge.com/VIDE/*

###### *[3] - PakRat - https://www.bagthorpe.org/bob/cofrdrbob/pakrat.html*

###### *[4] - Main code functionality plan - https://r00142.s-ul.eu/nea-bak/GVQ6YFl8*

###### *[5] - Overall code functionality plan - https://r00142.s-ul.eu/nea-bak/eStLKnHg*

###### *[6] - public/zip_uncompressed.h - https://hg.alliedmods.net/hl2sdks/hl2sdk-bgt/annotate/80044e1b14cc/public/zip_uncompressed.h*

###### *[7] - HxD - https://mh-nexus.de/en/hxd/*

###### *[8] - GCFscape - https://nemstools.github.io/pages/GCFScape-Download.html*

###### ***[9] -Structure parser parsing plan - https://r00142.s-ul.eu/nea-bak/tbFiB42H***