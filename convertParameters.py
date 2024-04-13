from LocalReadWriteMemory import ReadWriteMemory
from rallyProcess import getBotParameters
from util import parseJSON, readFile, toJSON, writeFile

botParameters = getBotParameters()

logsBest = readFile("./logs/logsBest_202404072212_Port_Soderick.json")

newLines = []
for line in logsBest.split("\n"):
    if line == "":
        continue
    o = parseJSON(line)
    params = o["params"]
    newParams = {}
    for key in params:
        i = int(key) - 1
        value = params[key]
        botParameter = botParameters[i]
        address = botParameter.address
        size = botParameter.size
        dataType = "int32"
        if size == 1:
            dataType = "int8"
        addressString = hex(address)
        newKey = f"{addressString}_{dataType}"
        newParams[newKey] = value
    newO = {
        "target": o["target"],
        "params": newParams
    }
    newLines.append(toJSON(newO))

writeFile("./logs/logsBest_202404081058_Port_Soderick.json", "\n".join(newLines))
