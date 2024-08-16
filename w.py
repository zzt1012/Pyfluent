import numpy as np
from pyDOE import lhs


def generate_lhs_samples(num_lev, Q_min, Q_max, beta_min, beta_max, file_path):
    # 生成拉丁超立方采样
    lhs_sample = lhs(2, samples=num_lev)

    # 计算 heat_flux 和 beta
    heat_flux = lhs_sample[:, 0] * (Q_max - Q_min) + Q_min
    beta = lhs_sample[:, 1] * (beta_max - beta_min) + beta_min

    # 打印结果
    print('heat_flux', heat_flux)
    print('beta', beta)

    # 保存结果到文件
    np.savetxt(file_path, np.column_stack((heat_flux, beta)))

    # 返回排序后的结果
    sorted_indices = np.lexsort((beta, heat_flux))
    sorted_heat_flux = heat_flux[sorted_indices]
    sorted_beta = beta[sorted_indices]

    return sorted_heat_flux, sorted_beta


# 使用示例
num_lev = 10
Q_min = 899
Q_max = 1301
beta_min = 59999
beta_max = 90001
file_path = 'sample.txt'

sorted_heat_flux, sorted_beta = generate_lhs_samples(num_lev, Q_min, Q_max, beta_min, beta_max, file_path)
print('Sorted heat_flux', sorted_heat_flux)
print('Sorted beta', sorted_beta)