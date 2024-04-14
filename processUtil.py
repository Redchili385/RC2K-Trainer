from util import int32, uint8
from time import sleep

def checkValues(ptrValues, process):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = int32(ptrValue[1])
        storedValue = int32(process.read(ptr))
        if value != storedValue:
            print(f"Error on writing bytes: {ptr:08x} {value:08x} {storedValue:08x}")
            return False
    return True

def ensureWrite(ptr, value, process):
    value = int32(value)
    process.write(ptr, value)
    while int32(process.read(ptr)) != value:
        print(f"value difference: { int32(process.read(ptr)):08x}{value:08x}")
        process.write(ptr, value)
        sleep(0.1)

def attemptWrites(ptrValues, process):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = int32(ptrValue[1])
        process.write(ptr, value)

def ensureWrites(ptrValues, process):
    attemptWrites(ptrValues, process)
    while not checkValues(ptrValues, process):
        print("Error on writing bytes, trying again")
        attemptWrites(ptrValues, process)

def readByte(ptr, process):
    return int(process.readByte(ptr)[0], base=16)

def ensureWriteByte(ptr, value, process):
    value = uint8(value)
    process.writeByte(ptr, [value])
    while readByte(ptr, process) != value:
        print(f"byte difference: {readByte(ptr, process):08x}{value:08x}")
        sleep(0.1)