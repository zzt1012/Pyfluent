import pandas as pd
import numpy as np
from scipy.io import savemat
import glob



#读取coords并处理数据
df_coords_ori = pd.read_excel('text.xlsx')
rows = df_coords_ori.values.tolist()
arrays_da = np.array([row[:3] for row in rows])
df_coords = arrays_da[np.argsort(arrays_da[:, 0])] #按照y排序



df_sorted = pd.DataFrame(df_coords, columns=['x', 'y', 'z'])

# 将排序后的数据保存到新的Excel文件
output_file_path = 'sorted_ori.xlsx'
df_sorted.to_excel(output_file_path, index=False)

print("Excel文件已排序并保存为新的文件。")




