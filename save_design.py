#在mat中新增design

import scipy
import os
import scipy.io as sio
import numpy as np

def get_involved_indices(folder_path):
    """
    提取 design.txt 中涉及的行索引，基于文件名中的索引。
    """
    involved_indices = []


    file_paths = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    for file_name in file_paths:
        try:
            # 提取文件名中的数字索引 i
            file_index = int(file_name.split('tps')[1].split('.txt')[0])  # 提取数字索引
            involved_indices.append(file_index)
        except ValueError:
            continue

    return involved_indices


def extract_design_data(design_file_path, indices):
    """
    提取 design.txt 中对应索引的数据，并将它们按行组合成 (4, 10) 的形状。
    """
    with open(design_file_path, 'r') as f:
        design_lines = f.readlines()

    extracted_data = []

    for i in indices:
        if i - 1 < len(design_lines):
            line = design_lines[i - 1].strip().split()
            extracted_data.append(list(map(float, line)))

    return np.array(extracted_data)


def update_mat_with_design(mat_file_path, design_data):
    """
    在已存在的 .mat 文件中添加 design 数据。
    """

    data = sio.loadmat(mat_file_path)
    data['design'] = design_data
    sio.savemat(mat_file_path, data)


folder_path = r"D:\pythonworks\test\aerogel_try"
design_file_path = r"D:\pythonworks\test\design.txt"
mat_file_path = r"D:\pythonworks\test\tps.mat"


involved_indices = get_involved_indices(folder_path)
print(f"Involved indices: {involved_indices}")


extracted_design_data = extract_design_data(design_file_path, involved_indices)
update_mat_with_design(mat_file_path, extracted_design_data)

updated_data = sio.loadmat(mat_file_path)


# 提取 'design' 数据并检查
if 'design' in updated_data:
    design = np.squeeze(updated_data['design'])
    print(f"Design data shape: {design.shape}")
else:
    print("'design' key not found in the updated .mat file.")

#------------------------------------------------------------

data = scipy.io.loadmat('tps.mat')
print("文件的键名:", data.keys())

coords = np.squeeze(data['coords'])
fields = np.squeeze(data['fields'])
design = np.squeeze(data['design'])


print(f"coords 的形状: {coords.shape}")
print(f"fields 的形状: {fields.shape}")
print(f"design 的形状: {design.shape}")
