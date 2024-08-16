import numpy as np
from pyDOE import lhs

def generate_samples(lhs_sample, min, max):
    design = lhs_sample * (max -min) +min

    return design

# 拉丁超立方采样数量
num_lev = 10000

# 参数的最小值和最大值
params = [
    (899, 1301),     # Q_min, Q_max
    (59999, 90001),  # beta_min, beta_max
    (10, 20),        # lx_min, lx_max (示例值，请根据实际情况替换)
    (5, 15),         # ly_min, ly_max (示例值，请根据实际情况替换)
    (1, 10)          # lz_min, lz_max (示例值，请根据实际情况替换)
]

# 拉丁超立方采样
lhs_sample = lhs(len(params), samples=num_lev)

# 使用循环生成样本数据
samples = np.zeros((num_lev, len(params)))
for i, (min_val, max_val) in enumerate(params):
    samples[:, i] = generate_samples(lhs_sample[:, i], min_val, max_val)

# 分别提取各个参数的样本数据
heat_flux, beta, lx, ly, lz = samples.T

print('heat_flux', heat_flux)
print('beta', beta)

np.savetxt('design.txt', samples)