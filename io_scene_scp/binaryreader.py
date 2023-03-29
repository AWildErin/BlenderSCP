from io import BufferedReader
import os, struct

def readString(file: BufferedReader) -> str:
    length = struct.unpack("i", file.read(4))[0]
    return file.read(length).decode()

def readChar(file: BufferedReader):
    return struct.unpack("c", file.read(1))[0]

def readInt(file: BufferedReader) -> int:
    return struct.unpack("i", file.read(4))[0]

def readFloat(file: BufferedReader) -> float:
    return struct.unpack("f", file.read(4))[0]