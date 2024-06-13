import pandas as pd
import numpy as np
from scipy.io import savemat
import glob

#将fluent导出的多个txt数据提取出，转成xlsx文件
tem = glob.glob('./data/save/tps5_*.txt')
data_tem = []

for tems in tem:
    df = pd.read_csv(tems)
    data_tem.append(df['temperature'])

data_tem = pd.concat(data_tem, axis=1)
data_tem.to_excel('./data/save/tps5_temp.xlsx', index=False)

heatflux_num = 5

#读取coords并处理数据
df_coords_ori = pd.read_excel('./data/save/tps5_coords.xlsx')
rows = df_coords_ori.values.tolist()
arrays_da = np.array([row[:3] for row in rows])
df_coords = arrays_da[np.argsort(arrays_da[:, 1])] #按照y排序

X = arrays_da[:, 0].reshape((40, 792))
Y = arrays_da[:, 1].reshape((40, 792))
Z = arrays_da[:, 2].reshape((40, 792))

coords = np.stack((X, Y, Z), axis=2)
coords_tile = np.tile(coords[None, :, :, :], (heatflux_num, 40, 792, 3))  #四维张量

#读取fields并处理数据
df_fields = pd.read_excel('./data/save/tps5_fields.xlsx')
#fields = np.stack([np.array(df_fields[col].tolist()).reshape((40, 792)) for col in ['Temperature']], axis=2)
fields = np.array(df_fields).reshape((40, 792))
fields_tile = np.tile(fields[None, :, :], (heatflux_num, 40, 792))  #三维张量

#保存成mat文件
savemat('tps_arogel.mat', {'coords': coords_tile, 'fields': fields_tile})

print('fields.shape', fields.shape)
print('coords.shape', coords.shape)

#取测点
a = fields[:, 0, 102, ::179]  #截取最外面的面，选取1/2y处，在厚度z方向等距取3个点

#散点图展示数据





