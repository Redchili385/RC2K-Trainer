
from processUtil import ensureWrite, ensureWriteByte, ensureWriteFloat, readByte, readFloat
from rallyUtil import getBotParameters

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
    for processBotParameter in processBotParametersByAddress.values():
        botParameter = processBotParameter.botParameter
        valuesDictKey = getKeyByBotParameter(botParameter)
        value = valuesDict[valuesDictKey]
        dataType = botParameter.dataType
        stepSize = botParameter.stepSize
        if dataType != "float32":
            value = int(round(value, 0))
            min = botParameter.minValue
            valueDiff = value - min
            valueDiff = valueDiff - valueDiff % stepSize
            value = min + valueDiff
        pointer = processBotParameter.pointer
        if dataType == "uint8":
            ensureWriteByte(pointer, value, process)
        if dataType == "int8":
            ensureWriteByte(pointer, value, process)
        if dataType == "int32":
            ensureWrite(pointer, value, process)
        if dataType == "float32":
            ensureWriteFloat(pointer, value, process)

def getBotParameterBounds(botParameter):
    return (botParameter.minValue, botParameter.maxValue)

def getKeyByBotParameter(botParameter):
    dataType = botParameter.dataType
    address = botParameter.address
    addressString = hex(address)
    return f"{addressString}_{dataType}"

def getBotParametersBounds(botParameters):
    result = {}
    for botParameter in botParameters:
        result[getKeyByBotParameter(botParameter)] = getBotParameterBounds(botParameter)
    return result

def getProcessBotParametersByAddress(processBotParameters):
    getProcessBotParametersByAddress = {}
    for processBotParameter in processBotParameters:
        address = processBotParameter.botParameter.address
        getProcessBotParametersByAddress[address] = processBotParameter
    return getProcessBotParametersByAddress
      