
from processUtil import ensureWrite, ensureWriteByte
from rallyUtil import getBotParameters

class ProcessBotParameter:
    def __init__(self, botParameter, process):
        self.pointer = process.get_pointer(botParameter.address)
        self.botParameter = botParameter

def getProcessBotParameters(process):
    return map(lambda botParameter: ProcessBotParameter(botParameter, process), getBotParameters())

def setBotParameters(processBotParameters, valuesDict, process):
    for index, processBotParameter in enumerate(processBotParameters):
        botParameter = processBotParameter.botParameter
        value = int(round(valuesDict[str(index+1)], 0))
        stepSize = botParameter.stepSize
        value = value * stepSize
        size = botParameter.size
        pointer = processBotParameter.pointer
        if size == 1:
            ensureWriteByte(pointer, value, process)
        if size == 4:
            ensureWrite(pointer, value, process)

def getBotParameterBounds(botParameter):
    return (botParameter.minValue, botParameter.maxValue)

def getBotParametersBounds(botParameters):
    result = {}
    for index, botParameter in enumerate(botParameters):
        result[str(index+1)] = getBotParameterBounds(botParameter)
    return result
      