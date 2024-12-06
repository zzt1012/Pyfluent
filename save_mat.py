#保存fluent计算后的多个txt成mat文件
import os
import numpy as np
import pandas as pd
import scipy.io as sio
import scipy


def process_file(file_path):
    """
    按照列的索引进行排序处理单个文件。
    """
    df = pd.read_csv(file_path, delimiter=',', header=None, skiprows=1)

    # 打印读取的数据的形状和前几行，检查列数
    print(f"Data shape for {file_path}: {df.shape}")
    print(df.head())  # 打印前几行以检查数据格式

    # 强制将所有数值列转换为浮动类型，避免非数值导致的排序问题
    df[1] = pd.to_numeric(df[1], errors='coerce')
    df[2] = pd.to_numeric(df[2], errors='coerce')
    df[3] = pd.to_numeric(df[3], errors='coerce')
    df[4] = pd.to_numeric(df[4], errors='coerce')

    # 每 262 * 253 行按列 1（x）排序
    sort_x = []
    for i in range(0, len(df), 262 * 253):
        group = df.iloc[i:i + 262 * 253]
        sorted_group = group.sort_values(by=1)
        sort_x.append(sorted_group)
    sorted_x_df = pd.concat(sort_x, ignore_index=True)

    # 每 262 * 20 行按列 3（z）排序
    sort_z = []
    for i in range(0, len(sorted_x_df), 262 * 20):
        group = sorted_x_df.iloc[i:i + 262 * 20]
        sorted_group = group.sort_values(by=3)
        sort_z.append(sorted_group)
    sorted_z_df = pd.concat(sort_z, ignore_index=True)

    # 每 262 行按列 2（y）排序
    sort_y = []
    for i in range(0, len(sorted_z_df), 262):
        group = sorted_z_df.iloc[i:i + 262]
        sorted_group = group.sort_values(by=2)
        sort_y.append(sorted_group)
    sorted_y_df = pd.concat(sort_y, ignore_index=True)

    # 温度 (253, 262, 20)
    temperature = sorted_y_df.iloc[:, 4].values.reshape(253, 262, 20)  # 提取温度（第五列）并reshape

    # 坐标 (253, 262, 20, 3)
    coords = np.stack([
        sorted_y_df.iloc[:, 1].values.reshape(253, 262, 20),  # x 坐标
        sorted_y_df.iloc[:, 2].values.reshape(253, 262, 20),  # y 坐标
        sorted_y_df.iloc[:, 3].values.reshape(253, 262, 20)  # z 坐标
    ], axis=-1)  # Stack to get shape (253, 262, 20, 3)

    return temperature, coords


def save_to_mat(fields, coords, output_path):
    """
    保存结果到 .mat 文件
    """
    sio.savemat(output_path, {'fields': fields.astype(np.float64), 'coords': coords.astype(np.float64)}, format='7.3')


def process_all_files(folder_path):
    """
    处理文件夹中的所有文件，并保存结果到 .mat 文件。
    """
    # 获取文件夹中所有 .txt 文件
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

    fields_results = []
    coords_results = []

    max_fields = -np.inf
    max_coords = -np.inf

    max_fields_file = ''
    max_coords_file = ''

    fields_results = []
    coords_results = []

    for file_path in file_paths:
        print(f"Processing {file_path}...")
        processed_data, coords_data = process_file(file_path)
        fields_results.append(processed_data)
        coords_results.append(coords_data)

        #jiancha
        field_max = np.max(processed_data)
        coords_max = np.max(coords_data)

        if field_max > max_fields:
            max_fields = field_max
            max_fields_file = file_path

        if coords_max > max_coords:
            max_coords = coords_max
            max_fields_file = file_path

        # 查找温度超过5000的元素
        high_temp_indices = np.where(processed_data > 5000)

        # 输出温度超过5000的元素及其位置
        if high_temp_indices[0].size > 0:
            print(f"File {file_path} contains temperature values > 5000:")
            for idx in range(len(high_temp_indices[0])):
                i, j, k = high_temp_indices[0][idx], high_temp_indices[1][idx], high_temp_indices[2][idx]
                temp_value = processed_data[i, j, k]
                print(f"  - Temperature: {temp_value} at position: ({i}, {j}, {k})")


    # (样本数, 253, 262, 20)
    fields_array = np.array(fields_results)
    coords_array = np.array(coords_results)

    save_to_mat(fields_array, coords_array, os.path.join(folder_path, 'tps.mat'))
    print("All files processed and saved to output_data.mat.")

    print(f"max valus:{max_fields} from file:{max_fields_file}")
    print(f"max valus:{max_coords} from file:{max_coords_file}")



folder_path = r"/data/ZZT/pythonworks/pyfluent/work/data_temp"
#folder_path = r'/home/admin/ZZT/python_program/save_data/test'
process_all_files(folder_path)

data = scipy.io.loadmat('/data/ZZT/pythonworks/pyfluent/work/data_temp/tps.mat')
#data = scipy.io.loadmat('/home/admin/ZZT/python_program/save_data/test/tps.mat')
print("Coords 文件的键名:", data.keys())

# 根据实际键名提取数据
coords = np.squeeze(data['coords'])
fields = np.squeeze(data['fields'])


print(f"coords 的形状: {coords.shape}")
print(f"fields 的形状: {fields.shape}")

#fields/coords
