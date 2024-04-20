from LocalReadWriteMemory import ReadWriteMemory
from rallyProcess import getProcessBotParameters, getProcessBotParametersByAddress, setProcessBotParametersToProcess
from rallyUtil import getBotParameters
from util import parseJSON, readFile

logsBestString = readFile("./logs/logs_202404152306_Port_Soderick.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

#logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[218]
print(bestLog)

botParameters = getBotParameters()


setProcessBotParametersToProcess(getProcessBotParametersByAddress(getProcessBotParameters(process)), bestLog["params"], process)