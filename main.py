import numpy as np

# 样本数量
num_samples = 4
#

# # 将样本值转换到指定范围
# samples1 = np.linspace(0,10,num_samples)
# samples2 = np.linspace(80,700,num_samples)
# print(samples2)
# print(samples1)

# 文件路径
file_path = 'sample.txt'

# 循环写入每个样本点，覆盖先前的数据
for i in range(num_samples):
    with open(file_path, 'w') as file:
        file.write(f"{samples1[i]:.4f}\t{samples2[i]:.4f}\n")
        print(samples1[i],samples2[i])
