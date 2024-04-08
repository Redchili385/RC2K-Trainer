from util import uint32
from time import sleep
from util import uint32

def checkValues(ptrValues, process):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = uint32(ptrValue[1])
        storedValue = process.read(ptr)
        if value != storedValue:
            return False
    return True

def ensureWrite(ptr, value, process):
    value = uint32(value)
    process.write(ptr, value)
    while process.read(ptr) != value:
        print(f"value difference: { process.read(ptr):08x}{value:08x}")
        process.write(ptr, value)
        sleep(0.1)

def attemptWrites(ptrValues, process):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = uint32(ptrValue[1])
        process.write(ptr, value)

def ensureWrites(ptrValues, process):
    attemptWrites(ptrValues, process)
    while not checkValues(ptrValues, process):
        print("Error on writing bytes, trying again")
        attemptWrites(ptrValues, process)

def ensureWriteByte(ptr, value, process):
    process.writeByte(ptr, [value])
    while int(process.readByte(ptr)[0], base=16) != value:
        print(f"byte difference: {int(process.readByte(ptr)[0], base=16):08x}{value:08x}")
        sleep(0.1)