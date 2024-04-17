from LocalReadWriteMemory import ReadWriteMemory
from rallyProcess import getProcessBotParameters, getProcessBotParametersByAddress, setProcessBotParametersToProcess
from util import parseJSON, readFile


rwm = ReadWriteMemory()
process = rwm.get_process_by_name("ral.exe")
process.open()

logsBestString = readFile("./logs/logs_202404152306_Port_Soderick.json")
logsBestStrings = logsBestString.split("\n")
logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]

#logsBestList.sort(key=lambda x: x["target"], reverse=True)
bestLog = logsBestList[218]
print(bestLog)

setProcessBotParametersToProcess(getProcessBotParametersByAddress(getProcessBotParameters(process)), bestLog["params"], process)

process.close()