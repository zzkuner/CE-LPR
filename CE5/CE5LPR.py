#
# import xml.etree.ElementTree as ET
# import numpy as np
# import matplotlib.pyplot as plt
#
# def parse_pds4_file(file_path):
#     # 加载和解析XML文件
#     tree = ET.parse(file_path)
#     root = tree.getroot()
#
#     # 处理命名空间
#     ns = {
#         'pds': 'http://pds.nasa.gov/pds4/pds/v1',
#         'sp': 'http://pds.nasa.gov/pds4/sp/v1'
#     }
#
#     # 获取File Area信息
#     file_area = root.find('pds:File_Area_Observational', ns)
#     file = file_area.find('pds:File', ns)
#     file_name = file.find('pds:file_name', ns).text
#
#     # 读取二进制数据
#     with open(file_name, 'rb') as f:
#         data = f.read()
#
#     # 解析科学数据
#     # 根据XML中的group_location和group_length
#     offset = 311
#     num_records = 132
#     record_length = 12311
#     num_samples = 3000
#     sample_size = 4  # 每个数据点占用4个字节
#
#     # 初始化数组
#     science_data = np.zeros((num_records, num_samples), dtype=np.float32)
#
#     # 读取科学数据
#     for i in range(num_records):
#         record_start = offset + i * record_length
#         for j in range(num_samples):
#             sample_start = record_start + j * sample_size
#             sample = np.frombuffer(data[sample_start:sample_start + sample_size], dtype=np.float32)
#             science_data[i, j] = sample[0]
#
#     # 绘制科学数据
#     plt.figure(figsize=(10, 6))
#     plt.imshow(science_data, cmap='viridis', aspect='auto')
#     plt.colorbar(label='Data Value')
#     plt.title('Science Data Image')
#     plt.xlabel('X Axis')
#     plt.ylabel('Y Axis')
#     plt.savefig('science_data_image.png')
#     plt.show()
#
# if __name__ == "__main__":
#     file_path = 'CE5-L_GRAS_LRPR-A_SCI_N_20201130092304_20201130094032_0001_A.2BL'  # 替换为你的文件路径
#     parse_pds4_file(file_path)

# import xml.etree.ElementTree as ET
# import numpy as np
# import matplotlib.pyplot as plt
# import os
# import struct
#
#
# def parse_pds4_file(xml_file_path):
#     # 加载和解析XML文件
#     tree = ET.parse(xml_file_path)
#     root = tree.getroot()
#
#     # 处理命名空间
#     ns = {
#         'pds': 'http://pds.nasa.gov/pds4/pds/v1',
#         'sp': 'http://pds.nasa.gov/pds4/sp/v1'
#     }
#
#     # 获取文件名
#     file_area = root.find('pds:File_Area_Observational', ns)
#     file_path = file_area.find('pds:File', ns).find('pds:file_name', ns).text
#
#     # 获取记录数
#     records = int(file_area.find('pds:File', ns).find('pds:records', ns).text)
#
#     # 获取增益状态 (假设在元数据中存储)
#     gain_state_element = root.find('pds:Gain_State', ns)  # 假设增益状态在该元素中
#     if gain_state_element is not None:
#         gain_state = float(gain_state_element.text)
#     else:
#         gain_state = 1.0  # 如果未找到增益状态，默认增益为 1.0
#
#     # 获取科学数据的二进制信息
#     table_binary = file_area.find('pds:Table_Binary', ns)
#     record_binary = table_binary.find('pds:Record_Binary', ns)
#     group_fields = record_binary.findall('pds:Group_Field_Binary', ns)
#
#     science_data_info = None
#     for group_field in group_fields:
#         if group_field.find('pds:name', ns).text == 'Science Data':
#             science_data_info = {
#                 'group_location': int(group_field.find('pds:group_location', ns).text),
#                 'group_length': int(group_field.find('pds:group_length', ns).text),
#                 'repetitions': int(group_field.find('pds:repetitions', ns).text),
#                 'field_length': int(group_field.find('pds:Field_Binary', ns).find('pds:field_length', ns).text),
#             }
#             break
#
#     if science_data_info is None:
#         raise ValueError("Science Data field not found in the PDS4 file.")
#
#     # 构造二进制文件的完整路径
#     binary_file_path = os.path.join(os.path.dirname(xml_file_path), file_path)
#
#     # 读取二进制数据
#     with open(binary_file_path, 'rb') as f:
#         data = f.read()
#
#     # 提取科学数据
#     start_index = science_data_info['group_location']
#     num_records = records
#     record_length = science_data_info['group_length']
#     num_samples = science_data_info['repetitions']
#     sample_size = science_data_info['field_length']
#
#     # 初始化数组
#     science_data = np.zeros((num_records, num_samples), dtype=np.float32)
#
#     # 读取科学数据
#     for i in range(num_records):
#         record_start = start_index + i * record_length
#         for j in range(num_samples):
#             sample_start = record_start + j * sample_size
#             # 假设科学数据是大端字节序存储的 float32
#             sample = struct.unpack('>f', data[sample_start:sample_start + sample_size])[0]
#             science_data[i, j] = sample
#
#     # 应用增益状态：乘以增益状态
#     science_data *= gain_state
#
#     # 打印科学数据的最大值和最小值，检查是否有异常值
#     print("科学数据的最大值：", np.max(science_data))
#     print("科学数据的最小值：", np.min(science_data))
#
#     # 处理无效值，转换NaN或无效数据为0，并设置数据上下限（例如去掉极大或极小的值）
#     science_data = np.nan_to_num(science_data, nan=0.0, posinf=0.0, neginf=0.0)
#
#     # 可以根据需要设置数据的上下限（这里我们假设科学数据的值在 0 到 1e6 之间合理）
#     science_data = np.clip(science_data, 0, 1e6)
#
#     # 绘制科学数据
#     plt.figure(figsize=(10, 6))
#     plt.imshow(science_data, cmap='viridis', aspect='auto')
#     plt.colorbar(label='Data Value')
#     plt.title('Science Data Image (with Gain State)')
#     plt.xlabel('X Axis')
#     plt.ylabel('Y Axis')
#     plt.savefig('science_data_image_with_gain.png')
#     plt.show()
#
#
# if __name__ == "__main__":
#     file_path = "CE5-L_GRAS_LRPR-A_SCI_N_20201130092304_20201130094032_0001_A.2BL"  # 文件路径
#     parse_pds4_file(file_path)

# import xml.etree.ElementTree as ET
# import numpy as np
# import matplotlib.pyplot as plt
# import os
# import struct
#
# def parse_pds4_file(xml_file_path):
#     # 加载和解析XML文件
#     tree = ET.parse(xml_file_path)
#     root = tree.getroot()
#
#     # 处理命名空间
#     ns = {
#         'pds': 'http://pds.nasa.gov/pds4/pds/v1',
#         'sp': 'http://pds.nasa.gov/pds4/sp/v1'
#     }
#
#     # 获取文件名
#     file_area = root.find('pds:File_Area_Observational', ns)
#     file_path = file_area.find('pds:File', ns).find('pds:file_name', ns).text
#
#     # 获取记录数
#     records = int(file_area.find('pds:File', ns).find('pds:records', ns).text)
#
#     # 解析其他相关参数，如道标识、收发标识、图像索引、时间码、道参数、道计数、数据长度、增益值等
#     channel_id = root.find('pds:Channel_Identifier', ns).text  # 道标识
#     transceiver_id = root.find('pds:Transceiver_Identifier', ns).text  # 收发标识
#     image_index = int(root.find('pds:Image_Index', ns).text)  # 图像索引
#     time_code = root.find('pds:Time_Code', ns).text  # 时间码
#     channel_params = root.find('pds:Channel_Parameters', ns).text  # 道参数
#     channel_count = int(root.find('pds:Channel_Count', ns).text)  # 道计数
#     data_length = int(root.find('pds:Data_Length', ns).text)  # 数据长度
#     gain_value = float(root.find('pds:Gain_Value', ns).text)  # 增益值
#
#     # 获取科学数据的二进制信息
#     table_binary = file_area.find('pds:Table_Binary', ns)
#     record_binary = table_binary.find('pds:Record_Binary', ns)
#     group_fields = record_binary.findall('pds:Group_Field_Binary', ns)
#
#     science_data_info = None
#     for group_field in group_fields:
#         if group_field.find('pds:name', ns).text == 'Science Data':
#             science_data_info = {
#                 'group_location': int(group_field.find('pds:group_location', ns).text),
#                 'group_length': int(group_field.find('pds:group_length', ns).text),
#                 'repetitions': int(group_field.find('pds:repetitions', ns).text),
#                 'field_length': int(group_field.find('pds:Field_Binary', ns).find('pds:field_length', ns).text),
#             }
#             break
#
#     if science_data_info is None:
#         raise ValueError("Science Data field not found in the PDS4 file.")
#
#     # 构造二进制文件的完整路径
#     binary_file_path = os.path.join(os.path.dirname(xml_file_path), file_path)
#
#     # 读取二进制数据
#     with open(binary_file_path, 'rb') as f:
#         data = f.read()
#
#     # 提取科学数据
#     start_index = science_data_info['group_location']
#     num_records = records
#     record_length = science_data_info['group_length']
#     num_samples = science_data_info['repetitions']
#     sample_size = science_data_info['field_length']
#
#     # 初始化数组
#     science_data = np.zeros((num_records, num_samples), dtype=np.float32)
#
#     # 读取科学数据
#     for i in range(num_records):
#         record_start = start_index + i * record_length
#         for j in range(num_samples):
#             sample_start = record_start + j * sample_size
#             # 假设科学数据是大端字节序存储的 float32
#             sample = struct.unpack('>f', data[sample_start:sample_start + sample_size])[0]
#             science_data[i, j] = sample
#
#     # 应用增益值
#     science_data *= gain_value
#
#     # 打印相关信息
#     print(f"道标识: {channel_id}, 收发标识: {transceiver_id}")
#     print(f"图像索引: {image_index}, 时间码: {time_code}")
#     print(f"道参数: {channel_params}, 道计数: {channel_count}")
#     print(f"数据长度: {data_length}, 增益值: {gain_value}")
#
#     # 绘制科学数据
#     plt.figure(figsize=(10, 6))
#     plt.imshow(science_data, cmap='viridis', aspect='auto')
#     plt.colorbar(label='Data Value')
#     plt.title(f'Science Data Image (Channel ID: {channel_id})')
#     plt.xlabel('X Axis')
#     plt.ylabel('Y Axis')
#     plt.savefig(f'science_data_image_channel_{channel_id}.png')
#     plt.show()
#
# if __name__ == "__main__":
#     file_path = "CE5-L_GRAS_LRPR-A_SCI_N_20201130092304_20201130094032_0001_A.2BL"  # 文件路径
#     parse_pds4_file(file_path)


import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt

def parse_pds4_file(file_path):
    # 加载和解析XML文件
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 处理命名空间
    ns = {
        'pds': 'http://pds.nasa.gov/pds4/pds/v1',
        'sp': 'http://pds.nasa.gov/pds4/sp/v1'
    }

    # 获取File Area信息
    file_area = root.find('pds:File_Area_Observational', ns)
    file = file_area.find('pds:File', ns)
    file_name = file.find('pds:file_name', ns).text

    # 读取二进制数据
    with open(file_name, 'rb') as f:
        data = f.read()

    # 解析科学数据
    # 根据XML中的group_location和group_length
    offset = 311-1
    num_records = 132
    record_length = 12311
    num_samples = 3000
    sample_size = 4  # 每个数据点占用4个字节

    # 初始化数组
    science_data = np.zeros((num_records, num_samples), dtype=np.float32)

    # 读取科学数据
    for i in range(num_records):
        record_start = offset + i * record_length
        for j in range(num_samples):
            sample_start = record_start + j * sample_size
            sample = np.frombuffer(data[sample_start:sample_start + sample_size], dtype='>f4')
            # sample=sample.astype('>f4')
            science_data[i, j] = sample[0]

    # 绘制科学数据
    plt.figure(figsize=(10, 6))
    # plt.imshow(science_data.T, cmap='viridis', aspect='auto')
    # plt.colorbar(label='Data Value')
    # plt.title('Science Data Image')
    # plt.xlabel('X Axis')
    # plt.ylabel('Y Axis')
    # plt.savefig('science_data_image.png')
    plt.plot(science_data[1,:])
    plt.show()

if __name__ == "__main__":
    file_path = 'CE5-L_GRAS_LRPR-A_SCI_N_20201201171559_20201201173326_0001_A.2BL'  # 替换为你的文件路径
    parse_pds4_file(file_path)