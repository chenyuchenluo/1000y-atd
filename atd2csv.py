# -*- coding: UTF-8 -*-

import os
import base64
from io import BytesIO
import csv

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(DIR_PATH,"output")
FILES_PATH = os.path.join(DIR_PATH,"atds")

BYTESTRINGSIZE = 255

def run():
	if not os.path.exists(FILES_PATH):
		print("ERROR! {} not exist.".format(FILES_PATH))
		exit()

	if not os.path.exists(OUT_PATH):
		os.makedirs(OUT_PATH)

	for root, dirs, files in os.walk(FILES_PATH):
		for file in files:
			strArr = file.split(".")
			if file[-3:].lower() != "atd":
				continue

			print("开始解析 {} 文件：".format(file))
			file_name = file[:-4]

			#缓冲区对象
			stream = BytesIO()

			with open(os.path.join(root,file),'rb') as f:
				content = f.read()
				stream.write(content)

			stream.seek(0)

			#开始读取
			count = len(stream.getbuffer()) / BYTESTRINGSIZE - 1
			# print('{} animation count {}'.format(file,count))
			if count < 1:
				print("{} 数据错误！".format(file))
				continue

			print("正在解析 {} 行数据".format(file))

			contents_json = "{\n\t\"version\":\"1.0.0\",\n\t\"actions\":[\n"
			Fields = []
			i = 0
			while i <= count:
				bytes_data = stream.read(BYTESTRINGSIZE)

				inverse_bytes = []
				j = 0
				while j < BYTESTRINGSIZE:
					inverse_bytes.append(inverse_byte_string(bytes_data[j]))
					j = j + 1

				longth = inverse_bytes[0]
				temp_bytes_data = inverse_bytes[1:longth + 1]
				# print(bytes(temp_bytes_data).decode('gbk'))

				temp_string = []
				chars = ''
				for x in temp_bytes_data:
					char = chr(x)
					if char == ',':
						temp_string.append(chars)
						chars = ''
						continue
					chars = chars + char

				# print(temp_string)
				if i == 0:
					Fields = temp_string
					i = i + 1
					continue

				if temp_string[0] == '':
					print("文件 {} 第{}行 无数据".format(file,i))
					i = i + 1
					continue

				# 填充正式内容
				contents_json = contents_json + "\t\t{\n"

				fcount = int(temp_string[3])
				contents_json = contents_json + "\t\t\t\"name\":\"{}\",\n".format(temp_string[1])
				contents_json = contents_json + "\t\t\t\"dir\":\"{}\",\n".format(temp_string[2])
				contents_json = contents_json + "\t\t\t\"frameCount\":{},\n".format(fcount)
				contents_json = contents_json + "\t\t\t\"frameTime\":{},\n".format(int(temp_string[4]))
				contents_json = contents_json + "\t\t\t\"frameInfo\":[\n"
				
				j = 0
				while j < fcount:
					idx = 5 + j * 3
					contents_json = contents_json + "\t\t\t\t{\n"
					frameIdx = temp_string[idx]
					if frameIdx == '':
						frameIdx = 0
					contents_json = contents_json + "\t\t\t\t\t\"frame\":{},\n".format(int(frameIdx))
					offset_x = temp_string[idx+1]
					if offset_x == '':
						offset_x = 0
					contents_json = contents_json + "\t\t\t\t\t\"px\":{},\n".format(int(offset_x))
					offset_y = temp_string[idx+2]
					if offset_y == '':
						offset_y = 0
					contents_json = contents_json + "\t\t\t\t\t\"py\":{},\n".format(int(offset_y))
					contents_json = contents_json + "\t\t\t\t},\n"
					j = j + 1

				contents_json = contents_json + "\t\t\t],\n\t\t},\n"

				i = i + 1

			contents_json = contents_json + "\t],\n}"
			stream.close()

			# out_csv_file = os.path.join(OUT_PATH,"{}.csv".format(file_name))
			# with open(out_csv_file,'w') as csv_file:
			# 	writer = csv.writer(csv_file)
			# 	writer.writerows(contents)

			out_json_file = os.path.join(OUT_PATH,"{}.json".format(file_name))
			with open(out_json_file,'w') as f:
				f.write(contents_json)

#交换高低位
def inverse_byte_string(val):
	return ((val & 0xF0) >> 4 & 0xFF) | ((val & 0x0F) << 4 & 0xFF)

run()

