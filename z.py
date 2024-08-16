import multiprocessing
import time

# 读取txt文件
file_path = 'design.txt'

with open(file_path, 'r') as file:
    lines = file.readlines()

# 提取设计变量的数量
num_lev = len(lines)

# 提取设计变量
heat_flux1 = []
heat_flux2 = []
beta = []
lx = []
ly = []
lz = []

for line in lines:
    h1, h2, b, x, y, z = map(float, line.split())
    heat_flux1.append(h1)
    heat_flux2.append(h2)
    beta.append(b)
    lx.append(x)
    ly.append(y)
    lz.append(z)

# 定义并行执行的函数
def process_design_variable(i):
    start_time = time.time()  # 记录每个case的开始时间

    print(f'****************************************\n第 {i} 个设计变量', heat_flux1[i], heat_flux2[i], beta[i], lx[i], ly[i], lz[i], '\n****************************************')

    with open(f'single_design_{i}.txt', 'w') as file:
        file.write(f'{heat_flux1[i]} {heat_flux2[i]} {beta[i]}\n')

    # 假设solver操作
    solver.tui.mesh.scale(lx[i] / lx[i], ly[i] / ly[i], lz[i] / lz[i])
    solver.tui.define.user_defined.compiled_functions('unload')
    solver.tui.define.user_defined.compiled_functions("compile", "liudf", "yes", "lamnda_eff.c")
    solver.tui.define.user_defined.compiled_functions("load")

    # 读取txt中数据
    solver.tui.define.user_defined.execute_on_demand('"read_file::liudf"')

    solver.tui.define.materials.change_create('nano', 'nano', 'yes', 'user-defined', '"rho::liudf"', 'no', 'yes', 'user-defined', '"lambda_eff::liudf"')
    solver.tui.define.boundary_conditions.wall('up', '0', 'no', '0', 'no', 'yes', 'heat-flux', 'yes', 'yes', '"udf"', '"heat_flux::liudf"', 'no', 'no', '1')

    # 初始化
    solver.tui.solve.initialize.reference_frame("relative")
    solver.tui.solve.initialize.set_defaults('temperature', '273.15')
    solver.tui.solve.initialize.initialize_flow('yes')

    print(f'****************************************\n第 {i} 次初始化结束\n****************************************')

    # 开始计算
    solver.tui.define.models.unsteady_2nd_order('yes')
    solver.tui.solve.set.transient_controls.time_step_size(0.01)
    solver.tui.solve.set.transient_controls.max_iterations_per_time_step(30)
    solver.tui.solve.set.transient_controls.number_of_time_steps(30)
    solver.tui.solve.dual_time_iterate()

    print(f'****************************************\n第 {i} 次已收敛\n****************************************')

    # udf保存数据
    solver.tui.define.user_defined.execute_on_demand('"save_file::liudf"')

    # 创建云图
    solver.results.graphics.contour['total_model'] = {"field": "temperature", "surfaces_list": ["behind", "down", "front", "left", "right", "up"]}
    solver.tui.display.objects.display('total_model')

    # 后处理
    solver.tui.file.export.ascii(f'work/data_temp/tps5_{i}.txt', (), 'yes', 'temperature', 'q', 'yes')
    solver.tui.file.write_case_data((f'work/tps/tps5_{i}.cas'))

    end_time = time.time()  # 记录每个case的结束时间
    duration = end_time - start_time
    print(f'****************************************\n第 {i} 个设计变量处理完成，耗时: {duration:.2f} 秒\n****************************************')

    return i

def main():
    num_cores = 40  # 使用40个核心
    num_threads = 10  # 10个线程组
    cases_per_thread = 1000  # 每个线程组处理1000个case

    total_start_time = time.time()  # 记录总的开始时间

    with multiprocessing.Pool(num_cores) as pool:
        # 分配任务给每个线程组
        for thread_num in range(num_threads):
            start_idx = thread_num * cases_per_thread
            end_idx = start_idx + cases_per_thread
            pool.map(process_design_variable, range(start_idx, end_idx))

    total_end_time = time.time()  # 记录总的结束时间
    total_duration = total_end_time - total_start_time
    print(f"并行计算完成，总耗时: {total_duration:.2f} 秒")

if __name__ == "__main__":
    main()