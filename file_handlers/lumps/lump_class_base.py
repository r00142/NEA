class LumpBaseParser():
    def __init__(self, fp, length):
        self._fp = fp
        self._lump_len = length
        self._lump_offset = self._fp.tell()

    def _init_fp(self):
        self._fp.seek(self._lump_offset, 0)
    
    def parse(self):
        print("not implemented")


class LumpBasePacker():
    def __init__(self, fp):
        self._fp = fp
        self._lump_offset = self._fp.tell()

    def _init_fp(self):
        self._fp.seek(self._lump_offset, 0)

    def pack(self):
        print("not implemented")
