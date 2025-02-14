import random
from datetime import datetime

import torch
from rallyProcess import RallyProcess
from rallySimpleBOTrainer import RallySimpleBOTrainer
from rallyTrainingResultsService import RallyTrainingResultsService
import gin
import logging
import os

#Initial configuration
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
logging.basicConfig(level=logging.DEBUG)
logging.debug("DEBUG: RC2K Trainer Started")
random.seed(datetime.now().ctime())
torch.set_printoptions(threshold=10_000)
gin.parse_config_file('default.gin')

#Opening Process because is seems always necessary in traner.py
process = RallyProcess("ral_botTraining_220424.exe")
initBotParameterValuesWithTargetList = RallyTrainingResultsService.loadBestBotParameterValuesList(
  "training-results/20240729.json"
)
trainer = RallySimpleBOTrainer(process, initBotParameterValuesWithTargetList)
trainer.train()

# if os.path.isfile("./logs/logsBest_20240413_Port_Soderick.json"):
#     load_logs(optimizer, logs=["./logs/logsBest_20240413_Port_Soderick.json"])
# else:




    