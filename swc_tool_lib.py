import os, os.path
import time
import numpy as np
import math
from skimage import io
import matplotlib.pyplot as plt
from openpyxl import Workbook

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import TensorDataset, DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score
from torch.utils.data import Dataset
from torchvision import datasets
# from torchvision.transforms import ToTensor, Lambda
import igraph as ig
from pylib.file_io import *
from sklearn.metrics import recall_score
# from sklearn.externals import joblib
import joblib
from sklearn import svm
from sklearn.model_selection import train_test_split
import queue
import Topology_scoring.metrics_delin as md
import glob

block_limit = [256, 256, 128]

# sys_path = "E://KaifengChen//neuTube_plus//"
# sys_path = "D://KaifengChen//neuTube_plus//"
sys_path = "C://Users//T7910//Desktop//KaifengChen//neuTube_plus//"


home_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//segments//"
test_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//segments_test//"
tiff_path = sys_path + "dataset//img//" + str(block_limit[0]) + "//tiff//"
tiffGS_path = sys_path + "dataset//swc//" + str(block_limit[0]) + "//tiff//"
swcGS_path = sys_path + "dataset//swc//" + str(block_limit[0]) + "//raw//"
ConnParam_path = sys_path + 'dataset//result//256//ConnParam.xlsx'
nn_model_path = sys_path + "dataset//result//256//model.pth"
conn_res_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//connector_result//"
origin_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//origin//"
svm_model_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//svm_model.m"
opt_scoring_path = sys_path + "dataset//result//" + str(block_limit[0]) + "//opt_scoring//"
topology_scoring_result = sys_path + "dataset//result//" + str(block_limit[0]) + "//opt_result.txt"


from swc_base import *
from keystructure_finder import *
from compare_GS import *
from calc_connect_parameter import *
from dataset import *
from learning import *
from connector_test import *
from calc_connect_parameter_v2 import *
from  svm_learning import *
from statistical_probability import *

