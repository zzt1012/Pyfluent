import subprocess

# -*- coding: utf-8 -*-
import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from matplotlib import pyplot
import os, sys
import csv
import math
import pandas as pd
import numpy as np
import argparse
import multiprocessing
import time
import numpy as np
from pyDOE import lhs
import ctypes

from wandb.docker import shell

num_lev = 100

# 定义边界条件和参数范围
design_ranges = {
    'Q1': (2000, 3000),
    'Q2': (1700, 2800),
    't1':(200, 500),
    't2':(1200, 1500),
    'lambda':(8e-6, 9e-6),
    'beta': (68670, 75898),
    'lx': (200, 500),
    'ly': (200, 500),
    'lz': (12.25, 73.50)
}

# latin超立方采样
np.random.seed(0)
lhs_sample = lhs(len(design_ranges), samples=num_lev)

# 生成参数
params = {}
for i, (key, (min_val, max_val)) in enumerate(design_ranges.items()):
    params[key] = lhs_sample[:, i] * (max_val - min_val) + min_val

# 保存到文件
data = np.column_stack([params[key] for key in design_ranges.keys()])


# 打印结果
for key, value in params.items():
    print(f'{key}: {value}\n')

subprocess.run(f"gcc receive_design.c -fPIC -shared -o compilamnda.so", shell = True, check = True)

for i in range(num_lev):
    arr = (ctypes.c_double * 6)(*data[i, :5])
    conct = ctypes.CDLL('./compilamnda.so')

    conct.receive_py(arr, 6)
