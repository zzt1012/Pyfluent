# Python调用fluent进行多工况计算







# 一、PyFluent介绍

PyFluent是PyAnsys（文档地址：https://docs.pyansys.com/）生态系统的一部分，其允许用户在Python环境中与其他PyAnsys库和其他外部Python库一起操纵使用Fluent。

用户可以使用PyFluent以编程的方式创建、交互和控制Fluent会话，以创建和定制工作区。此外还可以利用PyFluent通过高度可配置的定制脚本来提高工作效率。

PyFluent的主要模块`ansys-fluent-core`提供以下功能：

- 能够以串行或并行方式启动Fluent求解器，并使用`launching Fluent`模块连接到已运行的Fluent会话
- 能够编写Fluent Meshing功能脚本
- 能够使用Fluent的所有TUI命令编写脚本
- 能够异步运行多个Fluent会话
- 能够使用标准Python库（如matplotlib）以numpy arryas的形式检索Fluent的物理场数据，以实现自定义后处理
- 能够在Fluent的求解器事件上注册回调函数，例如可以在读取case或data文件时，或者Fluent求解器完成迭代时实现一些特殊的功能
- 能够使用MonitorsManager模块检索求解器监视器，例如残差



## 1、PyFluent API 接口及其使用

两种启动模式：Solution mode 和 Meshing mode

- solution mode类型的对象包括：

  - solver的对象：面向求解器的接口。它又包括：

    - TUI对象：Fluent求解器的文本界面的Python接口。

    - Root对象：与上述接口不同，是与outlinetree对应。



![image-20240126092445022](C:\Users\zt\AppData\Roaming\Typora\typora-user-images\image-20240126092445022.png)

# 二、代码展示及结果

## 1、代码展示

Pyfluet通过launch_fluent（）函数执行各组件的启动操作

```python
#启动fluent，载入网格，检查有无负体积网格

solver = pyfluent.launch_fluent(mode="solver",
                                version="3d",
                                precision="double",
                                processor_count=10,
                                show_gui=True)
solver.file.read(file_type="case", file_name="data/tps5_id6_x_t-new.cas")
solver.tui.mesh.check()
```

打开能量、辐射模型

```python
solver.setup.models.energy.enabled = True
solver.tui.define.models.radiation.rosseland('yes')
```

加载UDF文件

```python
#加载UDF文件
solver.tui.define.user_defined.use_built_in_compiler("yes")  #启用udf编译器
solver.tui.define.user_defined.compiled_functions("compile", "udf", "yes", "y", "radiation.c")  #编译udf源文件radiation.c
solver.tui.define.user_defined.compiled_functions("load","udf")  #加载udf
```

定义物性参数、边界条件、求解控制参数

```python
#solver.tui.define.materials.change_create('nano', 'nano', 'yes', 'constant', '370.', 'yes', 'constant', '700.', 'yes', 'constant', '0.03' )

parser = argparse.ArgumentParser()

parser.add_argument('--density', type=float, default=370., help='density')
parser.add_argument('--cp', type=float, default=700., help='cp')
parser.add_argument('--lamda', type=float, default=0.03, help='lamda')

parser.add_argument('--time_step_size', type=float, default=0.01, help='time_step_size')
parser.add_argument('--max_iterations_per_time_step', type=float, default=30, help='max_iterations_per_time_step')
parser.add_argument('--number_of_time_steps', type=float, default=30, help='number_of_time_steps')


args = parser.parse_args([])   #jupyter必须赋个初值

#物性参数
density = args.density
cp = args.cp
lamda = args.lamda

#iteration参数
time_step_size = args.time_step_size
max_iterations_per_time_step = args.max_iterations_per_time_step
number_of_time_steps = args.number_of_time_steps


solver.setup.materials.solid['nano'] = {'density': {'option': 'constant', 'value': density},
                                       'specific_heat': {'option': 'constant', 'value': cp},
                                        'thermal_conductivity': {'option': 'constant', 'value': lamda}}


heat_flux = [20000, 30000, 40000]

for index, q in enumerate(heat_flux):

    #solver.tui.define.boundary_conditions.wall('wall', 'up','0.01','no', '0.','no','yes', 'no', '{0}','no','no', '1' )
    solver.setup.boundary_conditions.wall['up'] = {'q': {'option': 'value', 'value': q}}
    

    #初始化：standard initialization
    #solver.tui.solve.initialize.compute_defaults.all_zones()
    solver.tui.solve.initialize.reference_frame("relative")
    solver.tui.solve.initialize.set_defaults('temperature','273.15')
    solver.tui.solve.initialize.initialize_flow('yes')  
    # solver.tui.solve.initialize.hyb_initialization()   hybrid initialization
    print('初始化结束')

    #开始计算
    solver.tui.define.models.unsteady_2nd_order()
    solver.tui.solve.set.transient_controls.time_step_size(time_step_size)
    solver.tui.solve.set.transient_controls.max_iterations_per_time_step(max_iterations_per_time_step)
    solver.tui.solve.set.transient_controls.number_of_time_steps(number_of_time_steps)
    solver.tui.solve.dual_time_iterate()

    #后处理
    solver.tui.file.write_case(('work/tps5_' + str(q)  + '.cas'))
    print('迭代完成')
```

模型退出

```python
solver.exit()
```

## 2、结果展示

![image-20240126095802355](C:\Users\zt\AppData\Roaming\Typora\typora-user-images\image-20240126095802355.png)

![Pic/微信图片_20240126100410.png)
