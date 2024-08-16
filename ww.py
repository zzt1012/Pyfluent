import numpy as np
import random

#latin超立方
num_lev = 4


heat_flux = np.linspace(80,700,num_lev)  # 用于存储读取的heat_flux值
beta =  np.linspace(0,10,num_lev)

print('heat_flux', heat_flux)
print('beta', beta)

sorted_heat_flux = np.sort(heat_flux)
sorted_beta = np.sort(beta)

np.savetxt('sapmle.txt', np.column_stack((sorted_heat_flux, sorted_beta)))

#加排序


