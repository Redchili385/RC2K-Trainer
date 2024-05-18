from time import sleep
import random
from datetime import datetime
import json

from botorch import fit_gpytorch_model
from gpytorch import ExactMarginalLogLikelihood
import torch
from LocalReadWriteMemory import ReadWriteMemory
from process import ensureWrite, ensureWrites, readFloat
from rallyProcess import RallyProcess, getBotParameters, getKeyByBotParameter, getProcessBotParameterValuesFromProcess, getProcessBotParameters, setProcessBotParametersToProcess
from rallyUtil import currentPlayerToPlayer0, getBotParametersBounds, getBotParametersByKey
from torchUtil import normalize, standardize, unnormalize
from util import parseJSON, readFile, selectMean
from gtbo.gaussian_process import robust_optimize_acqf
from gtbo.benchmarks import BoTorchFunctionBenchmark
from gtbo.gtbo import GTBO
from botorch.models import SingleTaskGP
from botorch.acquisition import UpperConfidenceBound
from botorch.test_functions.synthetic import SyntheticTestFunction, Ackley
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

# if os.path.isfile("./logs/logsBest_20240413_Port_Soderick.json"):
#     load_logs(optimizer, logs=["./logs/logsBest_20240413_Port_Soderick.json"])
# else:




    