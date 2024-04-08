from LocalReadWriteMemory import ReadWriteMemory
from rallyProcess import getBotParameters, setBotParameters
from util import parseJSON, readFile


rwm = ReadWriteMemory()
process = rwm.get_process_by_name("ral.exe")
process.open()

logsBestString = readFile("logsBest_202404072212_Port_Soderick.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[0]
print(bestLog)

setBotParameters(getBotParameters(process), bestLog["params"], process)

process.close()