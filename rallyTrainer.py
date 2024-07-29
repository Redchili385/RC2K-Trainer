from datetime import datetime
from math import sqrt
from rallyProcess import RallyProcess
from rallyUtil import getBotParameters, getBotParametersBounds, getBotParametersByKey
from util import parseJSON, readFile, selectMean

class RallyTrainer:
  def __init__(self, process: RallyProcess, initBotParameterValuesWithTargetList: "list[dict]" = None):
    self.process = process
    self.numberOfRunsPerEvaluation = 1
    self.mapName = "Arcade_2"
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
    self.process.holdCarOnStage()
    self.process.holdEnter()

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
        time = self.process.runArcade(self.botParameterByKey, args)
        speed = 100/time  # L/s   (L = Total Length in meters)
        scale = 10**8
        scaleSpeed = sqrt(scale)
        score = pow(speed * scaleSpeed, 2) # J * L /kg - Specific Kinectic Energy   
        scores.append(score) 
    return selectMean(1, scores)
    