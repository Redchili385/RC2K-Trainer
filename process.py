import struct
from util import int32, uint8
from time import sleep
from LocalReadWriteMemory import ReadWriteMemory

class Process:
    def __init__ (self, processName):
        rwm = ReadWriteMemory()
        self.rwmProcess = rwm.get_process_by_name(processName)
        self.rwmProcess.open()
        self.pointers = {}

    def __del__(self):
        self.rwmProcess.close()

    def getPointer(self, address):
        if address not in self.pointers:
            self.pointers[address] = self.rwmProcess.get_pointer(address)
        return self.pointers[address]
    
    def setPointer(self, address, pointer):
        self.pointers[address] = pointer
    
    def readInt32(self, address):
        return self.rwmProcess.read(self.getPointer(address))

    def writeInt32(self, address, value):
        self.rwmProcess.write(self.getPointer(address), value)

    def writeInt32Values(self, addrValues):
        for addrValue in addrValues:
            addr = addrValue[0]
            value = int32(addrValue[1])
            self.writeInt32(addr, value)

    def ensureWriteInt32(self, address, value):
        value = int32(value)
        ptr = self.getPointer(address)
        self.writeInt32(address, value)
        valueRead = int32(self.readInt32(ptr))
        while valueRead != value:
            print(f"value difference: { valueRead:08x}{value:08x}")
            self.writeInt32(ptr, value)
            sleep(0.1)
            valueRead = int32(self.readInt32(ptr))

    def checkValuesInt32(self, addrValues):
        for addrValue in addrValues:
            address = addrValue[0]
            value = int32(addrValue[1])
            storedValue = int32(self.readInt32(address))
            if value != storedValue:
                print(f"Error on writing bytes: {address:08x} {value:08x} {storedValue:08x}")
                return False
        return True
    
    def ensureWriteInt32Values(self, addrValues):
        self.writeInt32Values(addrValues)
        while not self.checkValuesInt32(addrValues):
            print("Error on writing bytes, trying again")
            self.writeInt32Values(addrValues)

    def readFloat(self, address):
        intValue = self.readInt32(address)
        bytes = struct.pack("<I", intValue)
        return struct.unpack("<f", bytes)[0]
    
    def writeFloat(self, address, value):
        bytes = struct.pack("<f", value)
        intValue = struct.unpack("<I", bytes)[0]
        self.writeInt32(address, intValue)

    def ensureWriteFloat(self, address, value):
        bytes = struct.pack("<f", value)
        intValue = struct.unpack("<I", bytes)[0]
        self.ensureWriteInt32(address, intValue)
    
    def readByte(self, address):
        process = self.rwmProcess
        ptr = self.getPointer(address)
        return int(process.readByte(ptr)[0], base=16)   

    def writeByte(self, address, value):
        process = self.rwmProcess
        ptr = self.getPointer(address)
        process.writeByte(ptr, [value])

    def ensureWriteByte(self, address, value):
        value = uint8(value)
        self.writeByte(address, value)
        while self.readByte(address) != value:
            print(f"byte difference: {self.readByte(address):08x}{value:08x}")
            sleep(0.1)