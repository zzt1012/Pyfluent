# -*- coding: utf-8 -*-
import threading

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


lock = threading.Lock()

num_lev = 100

length_x, length_y, length_z = 304.9406, 320.5, 24.50


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

# 保存数据到文件
data = np.column_stack([params[key] for key in design_ranges.keys()])

degrees_list = []

for i in range(num_lev):
    ld = 24.05997 * (params['lz'][i] / 24.5)
    radians = 2 * math.atan(params['lx'][i] / (2 * ld))
    degrees = math.degrees(radians)  #求弧度
    degrees_list.append(degrees)   #求角度
    print(params['lx'][i], params['lz'][i], degrees)

data_all = np.column_stack([data, degrees_list])

# 检查并创建输出目录
output_dir = './work/design'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

np.savetxt(os.path.join(output_dir, 'design.txt'), data_all, comments='')


def paraller_fluent(start_idx, end_idx):
 for i in range(start_idx, end_idx):
    # 启动fluent，载入网格，检查有无负体积网格
    solver = pyfluent.launch_fluent(mode="solver",
                                    version="3d",
                                    precision="double",
                                    processor_count=4,
                                    show_gui=True)

    solver.file.read(file_type="case", file_name="data/right_lat_0905.cas")
    solver.tui.mesh.check()

    pyfluent.logging.enable()  # 启用log日志

    solver.setup.models.energy.enabled = True


    start_time = time.time()  # 记录每个case的开始时间
    print('****************************************')
    print('设计变量：', *data[i, :])
    print('****************************************')

    with lock:
        with open(f'./work/index/design_.txt', 'w') as file:
            file.write(' '.join(map(str, data[i, :6])))

    solver.tui.mesh.scale(data[i, 6] / length_x, data[i, 7] / length_y, data[i, 8] / length_z)


    # 加载UDF文件
    with lock:
        #solver.tui.define.user_defined.compiled_functions('unload')
        solver.tui.define.user_defined.compiled_functions("compile", "secudf", "yes", "lamnda_eff.c")  # 编译udf源文件lambda.c
        solver.tui.define.user_defined.compiled_functions("load")  # 加载udf

        # 读取txt中数据
        solver.tui.define.user_defined.execute_on_demand('"read_file::secudf"')


    solver.tui.define.materials.change_create('nano', 'nano', 'yes', 'user-defined', '"rho::secudf"', 'no', 'yes',
                                              'user-defined', '"lambda_eff::secudf"')
    solver.tui.define.boundary_conditions.wall('up', '0', 'no', '0', 'no', 'yes', 'heat-flux', 'yes', 'yes', '"udf"',
                                               '"heat_flux_time::secudf"', 'no', 'no', '1')

    # 初始化：standard initialization
    # solver.tui.solve.initialize.compute_defaults.all_zones()

    solver.tui.solve.initialize.reference_frame("relative")
    solver.tui.solve.initialize.set_defaults('temperature', '273.15')
    solver.tui.solve.initialize.initialize_flow('yes')
    # solver.tui.solve.initialize.hyb_initialization()   hybrid initialization
    print('****************************************')
    print('第' + str(i) + '次初始化结束')
    print('****************************************')

    # 开始计算
    solver.tui.define.models.unsteady_2nd_order('yes')
    solver.tui.solve.set.transient_controls.time_step_size(10)
    solver.tui.solve.set.transient_controls.max_iterations_per_time_step(20)
    solver.tui.solve.set.transient_controls.number_of_time_steps(300)#300
    solver.tui.solve.dual_time_iterate()
    solver.tui.solve.iterate()

    print('****************************************')
    print('第' + str(i) + '次已收敛')
    print('****************************************')

    # udf保存数据
    #solver.tui.define.user_defined.execute_on_demand('"save_file::firudf"')

    # 创建云图
    solver.results.graphics.contour['total_model'] = {"field": "temperature",
                                                      "surfaces_list": ["behind", "down", "front", "left", "right",
                                                                        "up"]}
    solver.tui.display.objects.display('total_model')

    # 后处理
    solver.tui.file.export.ascii('work/data_temp/tps5_' + str(i+1)  + '.txt', (), 'yes', 'temperature', 'q', 'yes')

    # solver.tui.solve.dual_time_iterate('dual_time_iterate', '100', '20')
    solver.tui.file.write_case_data(('work/tps/tps5_' + str(i+1) + '.cas'))

    print('****************************************')
    print('第' + str(i+1) + '次数据保存结束')
    print('****************************************')

    end_time = time.time()  # 记录每个case的结束时间
    duration = end_time - start_time
    print(f'****************************************\n第 {i} 个设计变量处理完成，耗时: {duration:.2f} 秒\n****************************************')

    solver.exit()


if __name__ == "__main__":

   # num_cores = 40  # 使用40个核心
    num_threads = 10  # 10个线程组

    data_threads = num_lev // num_threads

    total_start_time = time.time()  # 记录总的开始时间

    with multiprocessing.Pool(num_threads) as pool:
        # # 分配任务给每个线程组
        for thread_num in range(num_threads):
            start_idx = thread_num * data_threads
            end_idx = start_idx + data_threads
            #pool.map(paraller_fluent, range(start_idx, end_idx))
            pool.apply_async(paraller_fluent, args=(start_idx, end_idx))
        ##pool.map(paraller_fluent, range(num_lev))

        pool.close()  # 关闭线程池，阻止再提交新的任务
        pool.join()  # 等待所有线程完成任务

    total_end_time = time.time()  # 记录总的结束时间
    total_duration = total_end_time - total_start_time
    print(f"并行计算完成，总耗时: {total_duration:.2f} 秒")
