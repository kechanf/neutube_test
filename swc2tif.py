import math

from skimage import io
import os, os.path
import tifffile
import numpy as np

# pixel_limit = [512,512,256] # 图像的最大像素
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

def get_point_dis(x1,y1,z1,x2,y2,z2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def get_point_dis_2d(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def brush_data(data, i, j, k):
    i = round(i)
    j = round(j)
    k = round(k)
    if(i<0 or i>511 or j<0 or j>511 or k<0 or k>255):
        # print("noonononoo")
        return data
    data[k][j][i] = 255
    return data

def simple_brush_soma(data):
    for i in range(256-10, 256+10):
        for j in range(256-10, 256+10):
            for k in range(128-10, 128+10):
                if(get_point_dis(i, j, k, 256, 256, 128) <= 5):
                    data = brush_data(data, i, j, k)
    return data

point_list = read_swc(test_file)
processed_tiff_path = home_path + test_file + '.tiff'
# if(os.path.isfile(processed_tiff_path)):
#     file = open(processed_tiff_path)
#     file.close()
# img = io.imread(processed_tiff_path)

data = np.zeros((256,512,512), 'uint8')
# print(data[255][511][511])
for point in point_list:
    point[2] = float(point[2])
    point[3] = float(point[3])
    point[4] = float(point[4])
    point[5] = 1.5 #float(point[5])

for point in point_list:
    x_range = range(round(point[2] - point[5]), round(point[2] + point[5]))
    y_range = range(round(point[3] - point[5]), round(point[3] + point[5]))
    z_range = range(round(point[4] - point[5]), round(point[4] + point[5]))

    for i in x_range:
        for j in y_range:
            for k in z_range:
                # print(i,j,k)
                if(get_point_dis(i,j,k,point[2],point[3],point[4]) < point[5]):
                    data = brush_data(data, i, j, k)

    # print(point[0], point[6])
    if(point[0] == point[6] or point[6] == -1):
        continue


    parent_point = point_list[int(point[6])-1]
    print(point[6])
    x_lower_range = point[2]
    x_upper_range = parent_point[2]
    y_lower_range = point[3]
    y_upper_range = parent_point[3]
    z_lower_range = point[4]
    z_upper_range = parent_point[4]
    r_lower_range = point[5]
    r_upper_range = parent_point[5]
    # print(x_upper_range, x_lower_range)
    for i in range(round(min(x_lower_range,x_upper_range)), round(max(x_lower_range,x_upper_range))):
        temp_x = i
        temp_y = y_lower_range + (i - x_lower_range)/(x_upper_range - x_lower_range) * (y_upper_range - y_lower_range)
        temp_z = z_lower_range + (i - x_lower_range)/(x_upper_range - x_lower_range) * (z_upper_range - z_lower_range)
        temp_r = r_lower_range + (i - x_lower_range)/(x_upper_range - x_lower_range) * (r_upper_range - r_lower_range)
        for j in range(round(temp_y - temp_r), round(temp_y + temp_r)):
            for k in range(round(temp_z - temp_r), round(temp_z + temp_r)):
                if(get_point_dis_2d(j, k, temp_y, temp_z) <= temp_r):
                    data = brush_data(data, i, j, k)

    for j in range(round(min(y_lower_range,y_upper_range)), round(max(y_lower_range,y_upper_range))):
        temp_x = x_lower_range + (j - y_lower_range)/(y_upper_range - y_lower_range) * (x_upper_range - x_lower_range)
        temp_y = j
        temp_z = z_lower_range + (j - y_lower_range)/(y_upper_range - y_lower_range) * (z_upper_range - z_lower_range)
        temp_r = r_lower_range + (j - y_lower_range)/(y_upper_range - y_lower_range) * (r_upper_range - r_lower_range)
        for i in range(round(temp_x - temp_r), round(temp_x + temp_r)):
            for k in range(round(temp_z - temp_r), round(temp_z + temp_r)):
                if(get_point_dis_2d(i, k, temp_x, temp_z) <= temp_r):
                    data = brush_data(data, i, j, k)

    for k in range(round(min(z_lower_range,z_upper_range)), round(max(z_lower_range,z_upper_range))):
        temp_x = x_lower_range + (k - z_lower_range)/(z_upper_range - z_lower_range) * (x_upper_range - x_lower_range)
        temp_y = y_lower_range + (k - z_lower_range)/(z_upper_range - z_lower_range) * (y_upper_range - y_lower_range)
        temp_z = k
        temp_r = r_lower_range + (k - z_lower_range)/(z_upper_range - z_lower_range) * (r_upper_range - r_lower_range)
        for i in range(round(temp_x - temp_r), round(temp_x + temp_r)):
            for j in range(round(temp_y - temp_r), round(temp_y + temp_r)):
                if(get_point_dis_2d(i, j, temp_x, temp_y) <= temp_r):
                    data = brush_data(data, i, j, k)


    # tifffile.imwrite('C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//segmentation//dir//temp'+ str(point[0]) +'.tif', data, photometric='minisblack')

data = simple_brush_soma(data)
tifffile.imwrite('temp.tif', data, photometric='minisblack')
tifffile.imwrite('C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//neutube_ws//example.tif', data, photometric='minisblack')










