from rallyExe import setBotParametersToExe
from rallyUtil import getBotParameters
from util import parseJSON, readFile

logsBestString = readFile("./logs/logs_202404220414_Port_Soderick.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

#logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[120]
print(bestLog)

botParameters = getBotParameters()

setBotParametersToExe(botParameters, bestLog["params"])