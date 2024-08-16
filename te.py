import numpy as np

file_path = "sample.txt"  # 替换为实际文件路径
num_lev = 4

heat_flux = np.linspace(80,700,num_lev)  # 用于存储读取的heat_flux值
beta =  np.linspace(0,10,num_lev)

with open(file_path, 'r') as file:
    lines = file.readlines()  # 读取所有行

for i in range(num_lev):
    # 读取第i行数据（i从0开始，所以是第i+1行）
    line = lines[i]
    heat_flux[i], beta[i] = map(float, line.split())  # 将两列数据转换为浮点数并存储
    print('第' + str(i) + '次', heat_flux[i], beta[i])