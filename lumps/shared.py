import codecs
import struct

def btoi_ul(bytearr):
    '''returns the input as an int, where the input is an unsigned little-endian'''
    return int.from_bytes(bytearr, "little", signed=False)

def btoi_sl(bytearr):
    '''returns the input as an int, where the input is a signed little-endian'''
    return int.from_bytes(bytearr, "little", signed=True)

def btoi_ub(bytearr):
    '''returns the input as an int, where the input is an unsigned big-endian'''
    return int.from_bytes(bytearr, "big", signed=False)

def btoi_sb(bytearr):
    '''returns the input as an int, where the input is a signed big-endian'''
    return int.from_bytes(bytearr, "big", signed=True)



def btof_ul(bytearr):
    '''returns the input as a float, where the input is an unsigned little-endian'''
    return struct.unpack("!f", ltob(bytearr))

def btof_ub(bytearr):
    '''returns the input as a float, where the input is an unsigned big-endian'''
    return struct.unpack("!f", bytearr)



def ltob(bytearr):
    '''returns the input as big endian, where the input is little endian'''
    output = b""
    output = output.join( [bytearr[x:x+1][::-1] for x in range(0,len(bytearr))] )[::-1]
    return output

def btot_l(bytearr):
    '''returns the input as a string, where the input is little-endian'''
    return ltob(bytearr).decode()

def btot_b(bytearr):
    '''returns the input as a string, where the input is little-endian'''
    return bytearr.decode()


