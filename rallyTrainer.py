from datetime import datetime
from rallyProcess import RallyProcess
from rallyUtil import getBotParameters, getBotParametersBounds, getBotParametersByKey
from util import parseJSON, readFile, selectMean

class RallyTrainer:
  def __init__(self, process: RallyProcess):
    self.process = process
    self.numberOfRunsPerEvaluation = 2
    self.mapName = "Port_Soderick"
    self.fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{self.mapName}.json"
    self.setUpGame()
    self.setInitialProperties()
    self.setBestParameters()
    self.botParameterValuesByKey = self.process.getBotParameterValuesByKey(self.botParameterByKey)

  def setUpGame(self):
    process = self.process
    process.ensureWriteInt32(process.pMaxWinTime, 3000000)
    process.ensureWriteInt32(process.pMaxWinTime2, 3000000)
    process.ensureWriteInt32(process.pFalseStartTime, 5000)

  def setInitialProperties(self):
    self.botParameters = getBotParameters()
    self.botParameterByKey = getBotParametersByKey(self.botParameters)
    self.botParametersBounds = getBotParametersBounds(self.botParameters)

  def setBestParameters(self, jsonParametersPath = "./logs/logs_202404240509_Port_Soderick.json", lineIndex = 75):
    logsBestString = readFile(jsonParametersPath)
    logsBestStrings = logsBestString.split("\n")
    logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]
    bestLog = logsBestList[lineIndex]
    print(bestLog["params"])
    self.process.setBotParameterValues(self.botParameterByKey, bestLog["params"])

  def black_box_function(self, **args):
    scores = []
    for i in range(self.numberOfRunsPerEvaluation):
        scores.append(self.process.runStage(self.botParameterByKey, args))
    return selectMean(1, scores)
    