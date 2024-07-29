from rallyExe import setBotParametersToExe
from rallyUtil import getBotParameters, getBotParametersByKey
from util import parseJSON, readFile

logsBestString = readFile("./logs/logs_202407290124_Arcade_2.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

#logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[143]
print(bestLog)

botParameters = getBotParametersByKey(getBotParameters())

setBotParametersToExe(botParameters, bestLog["params"])
