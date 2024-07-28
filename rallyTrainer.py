from datetime import datetime
from rallyProcess import RallyProcess
from rallyUtil import getBotParameters, getBotParametersBounds, getBotParametersByKey
from util import parseJSON, readFile, selectMean

class RallyTrainer:
  def __init__(self, process: RallyProcess, initBotParameterValuesWithTargetList: "list[dict]" = None):
    self.process = process
    self.numberOfRunsPerEvaluation = 2
    self.mapName = "Parkanaur"
    self.fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{self.mapName}.json"
    self.setUpGame()
    self.setInitialProperties()
    self.initBotParameterValuesList = [
      self.process.getBotParameterValuesByKey(self.botParameterByKey),
    ]
    if initBotParameterValuesWithTargetList is not None:
      self.setBestParameters(initBotParameterValuesWithTargetList)
      for initBotParameterValuesWithTarget in initBotParameterValuesWithTargetList:
        botParameterValues = {k: initBotParameterValuesWithTarget["params"][k] for k in initBotParameterValuesWithTarget["params"] if k in self.botParameterByKey}
        self.initBotParameterValuesList.append(botParameterValues)

  def setUpGame(self):
    process = self.process
    process.ensureWriteInt32(process.pMaxWinTime, 3000000)
    process.ensureWriteInt32(process.pMaxWinTime2, 3000000)
    process.ensureWriteInt32(process.pFalseStartTime, 5000)

  def setInitialProperties(self):
    self.botParameters = getBotParameters()
    self.botParameterByKey = getBotParametersByKey(self.botParameters)
    self.botParametersBounds = getBotParametersBounds(self.botParameters)

  def setBestParameters(self, botParameterValuesWithTargetList):
    bestBotParameterValuesWithTarget = max(botParameterValuesWithTargetList, key=lambda botParameterValuesWithTarget: botParameterValuesWithTarget["target"])
    self.process.setBotParameterValues(self.botParameterByKey, bestBotParameterValuesWithTarget["params"])

  def black_box_function(self, **args):
    scores = []
    for i in range(self.numberOfRunsPerEvaluation):
        scores.append(self.process.runStage(self.botParameterByKey, args))
    return selectMean(1, scores)
    