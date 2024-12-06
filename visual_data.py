#可视化3d图片

import os
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 指定 .mat 文件的路径（替换为你的文件路径）
coords_path = r'D:\pythonworks\test\tps.mat'

# 加载 .mat 文件数据
data = sio.loadmat(coords_path)

# 打印文件中的键名以确认数据存储的键名
print("mat 文件的键名:", data.keys())


# 根据实际键名提取数据
coords = np.squeeze(data['coords'])
fields = np.squeeze(data['fields'])
design = np.squeeze(data['design'])

# 检查数据的形状
print(f"coords 的形状: {coords.shape}")
print(f"fields 的形状: {fields.shape}")
print(f'design 的形状: {design.shape}')

# 处理坐标数据，将每三个数作为一个坐标点
coords_flattened = coords[0, :, :, :].reshape(-1, 3)  # 将坐标数据展平成每行3个元素的二维数组


# 创建 3D 图形
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')


sc = ax.scatter(coords_flattened[:, 0], coords_flattened[:, 1], coords_flattened[:, 2], c=fields[0, :, :], cmap='coolwarm', s=50)

cbar = plt.colorbar(sc, ax=ax, shrink=0.5, aspect=10)
cbar.set_label('Temperature/K')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title('3D-TPS')

plt.show()
