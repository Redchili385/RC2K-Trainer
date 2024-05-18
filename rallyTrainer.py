from datetime import datetime
import torch
from rallyProcess import RallyProcess
from rallyUtil import getBotParameters, getBotParametersBounds, getBotParametersByKey
from util import selectMean

class RallyTrainer:
  def __init__(self, process: RallyProcess):
    self.process = process
    self.numberOfRunsPerEvaluation = 2
    self.mapName = "Port_Soderick"
    self.fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{self.mapName}.json"
    self.setUpGame()
    self.setInitialProperties()

  def setUpGame(self):
    process = self.process
    process.setBestParameters()
    process.ensureWriteInt32(process.pMaxWinTime, 3000000)
    process.ensureWriteInt32(process.pMaxWinTime2, 3000000)
    process.ensureWriteInt32(process.pFalseStartTime, 5000)

  def setInitialProperties(self):
    self.botParameters = getBotParameters()
    self.botParameterByKey = getBotParametersByKey(self.botParameters)
    self.botParametersBounds = getBotParametersBounds(self.botParameters)

  def black_box_function(self, **args):
    scores = []
    for i in range(self.numberOfRunsPerEvaluation):
        scores.append(self.process.runStage(self.botParameterByKey, args))
    return selectMean(1, scores)
    