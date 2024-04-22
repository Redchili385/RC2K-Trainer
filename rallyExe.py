

from exeUtil import writeInt32 as exeWriteInt32, writeByte as exeWriteByte, writeFloat as exeWriteFloat
from rallyUtil import setBotParameters

rallyExePath = "./ral.exe"

def getExeAddress(processAddress):
  if processAddress > 0x4e0000:
    return processAddress + 0xde400 - 0x4e0000
  return processAddress - 0x400C00

def setBotParametersToExe(botParametersByAddress, valuesDict):
    exePath = rallyExePath
    def write(processAddress, value):
        exeAddress = getExeAddress(processAddress)
        exeWriteInt32(exeAddress, value, exePath)
    def writeByte(processAddress, value):
        exeAddress = getExeAddress(processAddress)
        exeWriteByte(exeAddress, value, exePath)
    def writeFloat(processAddress, value):
        exeAddress = getExeAddress(processAddress)
        exeWriteFloat(exeAddress, value, exePath)
    setBotParameters(botParametersByAddress, valuesDict, write, writeByte, writeFloat)