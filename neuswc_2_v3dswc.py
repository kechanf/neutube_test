import math

from skimage import io
import os, os.path
import tifffile
import numpy as np

pixel_limit = [512,512,256] # 图像的最大像素
# home_path = 'C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//segmentation//'
# test_file = "3500_2145_3271"

def read_swc(swc_name):
    with open(swc_name, 'r' ) as f:
        lines = f.readlines()

    point_number = -1
    point_list = []
    list_map = np.zeros(500000)


    for line in lines:
        if(line[0] == '#'):
            continue

        tem_line = line.split()
        # print(tem_line)
        point_list.append(tem_line)

        point_number = point_number + 1
        list_map[int(tem_line[0])] = point_number

    # print(point_list)
    return (point_list, list_map)

def neuswc_2_v3dswc(filePath, fileName):
    processed_swc_path = str(os.path.join(filePath, fileName))
    processed_swc_path = processed_swc_path[0:-4] + "_forv3d.swc"
    if (os.path.isfile(processed_swc_path)): # 处理过了
        return False

    point_list, list_map = read_swc(os.path.join(filePath, fileName))
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

    return True

if __name__ == "__main__":
    # home_path = 'C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//neutube_ws2//testdir_1//'
    home_path = 'E://crop_16bit_test/'
    processed_num = 0
    for filepath, dirnames, filenames in os.walk(home_path):
        for filename in filenames:
            if("_traced.swc" not in filename):
                continue
            if("forv3d.swc" in filename):
                continue

            file_AbsolutePath = os.path.join(filepath, filename)
            print(file_AbsolutePath)
            if(neuswc_2_v3dswc(filepath, filename)):
                processed_num = processed_num + 1
                print(str(processed_num) + " files had been processed!\n")











