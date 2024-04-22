
from processUtil import ensureWrite, ensureWriteByte, ensureWriteFloat, readByte, readFloat
from rallyUtil import getBotParameters, getKeyByBotParameter, setBotParameters

class ProcessBotParameter:
    def __init__(self, botParameter, process):
        self.pointer = process.get_pointer(botParameter.address)
        self.botParameter = botParameter

def getProcessBotParameters(process):
    return list(map(lambda botParameter: ProcessBotParameter(botParameter, process), getBotParameters()))

def getProcessBotParameterValuesFromProcess(processBotParametersByAddress, process):
    valuesDict = {}
    for processBotParameter in processBotParametersByAddress.values():
        botParameter = processBotParameter.botParameter
        valuesDictKey = getKeyByBotParameter(botParameter)
        dataType = botParameter.dataType
        pointer = processBotParameter.pointer
        if dataType == "uint8":
            value = readByte(pointer, process)
        if dataType == "int8":
            value = readByte(pointer, process)
            if value > 127:
                value = value - 256
        if dataType == "int32":
            value = process.read(pointer)
            if value > 0x7fffffff:
                value = value - 0x100000000
        if dataType == "float32":
            value = readFloat(pointer, process)
        valuesDict[valuesDictKey] = value
    return valuesDict

def setProcessBotParametersToProcess(processBotParametersByAddress, valuesDict, process):
    def write(address, value):
        pointer = processBotParametersByAddress[address].pointer
        ensureWrite(pointer, value, process)
    def writeByte(address, value):
        pointer = processBotParametersByAddress[address].pointer
        ensureWriteByte(pointer, value, process)
    def writeFloat(address, value):
        pointer = processBotParametersByAddress[address].pointer
        ensureWriteFloat(pointer, value, process)
    botParametersByAddress = {}
    for key, value in processBotParametersByAddress.items():
        botParametersByAddress[key] = value.botParameter
    setBotParameters(botParametersByAddress, valuesDict, write, writeByte, writeFloat)
      