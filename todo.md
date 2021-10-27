TODO:

- fix parsing custom assets from VMTs (relative paths, not absolute from /tf/)
- - Implement l40 delete file(s) function
  - Parse VPKs to find what is used in them --- do this in conjunction with checking folders for potential overrides
- Ignore/group `sp(_hdr)_*.vtf` files for easier viewing, same with `materials/maps/c*.hdr.vtf` files
  - Read references to files in VMTs (and RES?) files to smartly collect all needed files - **VMT DONE**
- Parsing PCF files to find where referenced particle systems exist
- Clean up structure parser library code (e.g. check the usage of enums, define 'special' vs 'basic' types in dicts, etc)
- Repacking
- Autopack or generate particle manifests
- Get more bsp test data
- Let the structure parser check if repeats of arrays or lengths of varlens match the values of other datatypes if set - raise an error if not.
