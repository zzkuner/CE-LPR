import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import struct
# XML文件路径
# xml_file = 'CE4_GRAS_LPR-2B_SCI_N_20201219044001_20201220084500_0163_A.2BL'
xml_file = 'CE4_GRAS_LPR-2A_SCI_N_20201119112501_20201120143000_0155_A.2BL'

# 解析XML文件
tree = ET.parse(xml_file)
root = tree.getroot()

# 定义命名空间
namespaces = {
    'pds': 'http://pds.nasa.gov/pds4/pds/v1',
    'sp': 'http://pds.nasa.gov/pds4/sp/v1'
}

# 获取Identification_Area信息
identification_area = root.find('pds:Identification_Area', namespaces)
logical_identifier = identification_area.find('pds:logical_identifier', namespaces).text
version_id = identification_area.find('pds:version_id', namespaces).text
title = identification_area.find('pds:title', namespaces).text
print(f"Logical Identifier: {logical_identifier}")
print(f"Version ID: {version_id}")
print(f"Title: {title}")

# 获取Observation_Area信息
observation_area = root.find('pds:Observation_Area', namespaces)
start_date_time = observation_area.find('pds:Time_Coordinates/pds:start_date_time', namespaces).text
stop_date_time = observation_area.find('pds:Time_Coordinates/pds:stop_date_time', namespaces).text
print(f"Start Date Time: {start_date_time}")
print(f"Stop Date Time: {stop_date_time}")

# 获取Mission_Area信息
mission_area = observation_area.find('pds:Mission_Area', namespaces)
product_id = mission_area.find('pds:product_id', namespaces).text
product_version = mission_area.find('pds:product_version', namespaces).text
product_level = mission_area.find('pds:product_level', namespaces).text
instrument_name = mission_area.find('pds:instrument_name', namespaces).text
print(f"Product ID: {product_id}")
print(f"Product Version: {product_version}")
print(f"Product Level: {product_level}")
print(f"Instrument Name: {instrument_name}")

# 获取Lander_Location信息
lander_location = mission_area.find('pds:Lander_Location', namespaces)
longitude = lander_location.find('pds:longitude', namespaces).text
latitude = lander_location.find('pds:latitude', namespaces).text
print(f"Lander Longitude: {longitude}")
print(f"Lander Latitude: {latitude}")

# # 获取File_Area_Observational信息
file_area = root.find('pds:File_Area_Observational', namespaces)
# 解析文件信息
file = file_area.find('pds:File', namespaces)
file_name = file.find('pds:file_name', namespaces).text
creation_date_time = file.find('pds:creation_date_time', namespaces).text
file_size = file.find('pds:file_size', namespaces).text
print(f"File Name: {file_name}")
print(f"Creation Date Time: {creation_date_time}")
print(f"File Size: {file_size}")

binary_file = file_name
# 打开二进制文件并读取所有数据
with open(binary_file, 'rb') as bin_file:
    data = bin_file.read()
# 解析记录二进制信息
table_binary = file_area.find('pds:Table_Binary', namespaces)
if table_binary is not None:
    record_binary = table_binary.find('pds:Record_Binary', namespaces)
    if record_binary is not None:
        # 遍历Record_Binary下的所有Field_Binary元素
        for field_binary in record_binary.findall('pds:Field_Binary', namespaces):
            # 获取name元素
            name_element = field_binary.find('pds:name', namespaces)
            if name_element is not None:
                field_name = name_element.text
                print(f"Field Name: {field_name}")
            else:
                print("Name element not found.")

            # 获取field_location元素
            field_location_element = field_binary.find('pds:field_location', namespaces)
            if field_location_element is not None:
                field_location = int(field_location_element.text)
                print(f"field_location: {field_location}")
            else:
                print("field_location_element not found.")

            # 获取data_type元素
            data_type_element = field_binary.find('pds:data_type', namespaces)
            if data_type_element is not None:
                data_type = data_type_element.text
                print(f"data_type: {data_type}")
            else:
                print("data_type_element not found.")

            # 获取field_length元素
            field_length_element = field_binary.find('pds:field_length', namespaces)
            if field_length_element is not None:
                field_length = int(field_length_element.text)
                print(f"Field_length: {field_length}")
            else:
                print("field_length_element not found.")

        group_field = record_binary.find('pds:Group_Field_Binary', namespaces)
        if group_field is not None:
            group_name = group_field.find('pds:name', namespaces).text
            repetitions = int(group_field.find('pds:repetitions', namespaces).text)
            fields = int(group_field.find('pds:fields', namespaces).text)
            groups = int(group_field.find('pds:groups', namespaces).text)
            group_location = int(group_field.find('pds:group_location', namespaces).text)
            group_length = int(group_field.find('pds:group_length', namespaces).text)
            group_field_binary =group_field.find('pds:Field_Binary', namespaces)
            group_field_length =int(group_field_binary.find('pds:field_length', namespaces).text)
            # 准备存储解析后的数据
            science_data = np.zeros(repetitions, dtype=np.float32)
            # 遍历group指定的次数
            for i in range(repetitions):
                sample_start = group_location -1 + i * group_field_length# 每个样本大小为4字节
                sample = np.frombuffer(data[sample_start:sample_start + group_field_length], dtype='<f4')  # 小端序
                science_data[i] = sample[0]
            plt.plot(science_data[:])
            plt.show()
        else:
            print("Group_Field_Binary element not found.")
    else:
        print("Record_Binary element not found.")
else:
    print("Table_Binary element not found.")