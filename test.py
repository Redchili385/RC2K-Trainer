# import struct

# def writeFloat(value):
#     bytes = struct.pack("<f", value)
#     intValue = struct.unpack("<I", bytes)[0]
#     print(intValue)

# def floatToInt(f, min, stepSize):
#     value = int(round(f, 0))
#     valueDiff = value - min
#     valueDiff = valueDiff - valueDiff % stepSize
#     return min + valueDiff

# writeFloat(-0.6)
# print(0x9E3738)
# print(f"{floatToInt(10368829.1, 0x9E3738, 4):08x}")

#from exeUtil import writeFloat
#from rallyExe import getExeAddress

#print(f"0x{getExeAddress(0x71bf38):08x}")
#riteByte("./ral.exe", 0x15, 2)

for (addr, value) in (5, 3):
  print(addr)
  print(value)