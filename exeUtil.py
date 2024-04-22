import struct

def writeInt32(address, value, path):
    with open(path, "rb+") as f:
        f.seek(address)
        f.write(struct.pack("<I", value))

def writeByte(address, value, path):
    if value < 0:
        value = 256 + value
    with open(path, "rb+") as f:
        f.seek(address)
        f.write(struct.pack("<B", value))

def writeFloat(address, value, path):
    with open(path, "rb+") as f:
        f.seek(address)
        f.write(struct.pack("<f", value))
        