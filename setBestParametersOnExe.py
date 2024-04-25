from rallyExe import setBotParametersToExe
from rallyUtil import getBotParameters, getBotParametersByAddress
from util import parseJSON, readFile

logsBestString = readFile("./logs/logs_202404240509_Port_Soderick.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

#logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[75]
print(bestLog)

botParameters = getBotParametersByAddress(getBotParameters())

setBotParametersToExe(botParameters, bestLog["params"])