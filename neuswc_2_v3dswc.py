import math

from skimage import io
import os, os.path
import tifffile
import numpy as np

pixel_limit = [512,512,256] # 图像的最大像素
home_path = 'C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//segmentation//'
test_file = "3822_1989_3217"

def read_swc(swc_name):
    with open( home_path + swc_name + '.swc', 'r' ) as f:
        lines = f.readlines()

    # point_number = 0
    point_list = []

    for line in lines:
        if(line[0] == '#'):
            continue
        # point_number = point_number + 1
        tem_line = line.split()
        # print(tem_line)
        point_list.append(tem_line)

    # print(point_list)
    return point_list

point_list = read_swc(test_file)
processed_swc_path = home_path + test_file + '_processed.swc'
# if(os.path.isfile(processed_tiff_path)):
#     file = open(processed_tiff_path)
#     file.close()
# img = io.imread(processed_tiff_path)

# data = np.zeros((256,512,512), 'uint8')
# print(data[255][511][511])

file = open(processed_swc_path,'w')
for point in point_list:
    point[3] = str(pixel_limit[2] - 1 - float(point[3]))
    # print(point)
    file.write(str(" ".join(point)))
    file.write("\n")

# if(os.path.isfile(processed_swc_path)):

# print(point_list)
# file.write(str(point_list))
file.close()













