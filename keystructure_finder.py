from swc_tool_lib import *

debug_mode = 0

def MinFiberEndDist(swcFiberA, swcFiberB, swcPoint_list):
    min_dist = -1
    connect_center = []
    for Ae in swcFiberA.sp:
        for Be in swcFiberB.sp:
            temp_dist = CalcswcPointDist(swcPoint_list[Ae], swcPoint_list[Be])
            if(min_dist == -1 or temp_dist < min_dist):
                min_dist = temp_dist
                connect_center = [
                    (swcPoint_list[Ae].x + swcPoint_list[Be].x) / 2,
                    (swcPoint_list[Ae].y + swcPoint_list[Be].y) / 2,
                    (swcPoint_list[Ae].z + swcPoint_list[Be].z) / 2
                ]
    return min_dist, connect_center

def KeyStructureFinder(swcFiber_list, swcPoint_list, filename, dist_tho = 10):
    file_count = 0
    test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//test.swc"
    for i in range(1, len(swcFiber_list)):
        swcFiberA = swcFiber_list[i]
        if(swcFiberA.l <= 2):
            continue

        # for temp_ep in swcFiberA.ep:
        for temp_sp in swcFiberA.sp:
            poss_connect = []
            for j in range(i + 1, len(swcFiber_list)):
                swcFiberB = swcFiber_list[j]
                if(swcFiberB.l <= 2):
                    continue
                min_dist = min(
                    CalcswcPointDist(swcPoint_list[temp_sp], swcPoint_list[swcFiberB.ep[0]]),
                    CalcswcPointDist(swcPoint_list[temp_sp], swcPoint_list[swcFiberB.ep[1]])
                )

                if(min_dist <= dist_tho):
                    poss_connect.append(swcFiberB)
            if(len(poss_connect) > 1):
                # print("!!!")
                # swcPoint_list[temp_sp].Printswc()
                file_count = file_count + 1
                filepath = test_filepath[0:-8] + filename + \
                           "_fiber%d&fiber%d"%(swcFiberA.fn, swcFiberB.fn) + \
                           "_poss_connect=%d"%(len(poss_connect)) + \
                           ".swc" # "_disttho=%d" % (dist_tho) + \

                # print(filepath)
                swcFiberA.Writeswc(filepath, swcPoint_list)
                for swcFiberB in poss_connect:
                    swcFiberB.Writeswc(filepath, swcPoint_list)

def CheckLimit(x, limit):
    if(x < 0):
        x = 0
    if(x > limit - 1):
        x = limit - 1
    return x

def FiberGSCheck(temp_swcFiber, swcPoint_list, img, percent_tho = 0.8):
    GS_sample_count = 0
    for sp in temp_swcFiber.sp:
        temp_x = CheckLimit(round(swcPoint_list[sp].x), block_limit[0])
        temp_y = CheckLimit(round(swcPoint_list[sp].y), block_limit[1])
        temp_z = CheckLimit(round(swcPoint_list[sp].z), block_limit[2])
        # print(temp_x, temp_y, temp_z)
        # print(img.shape)
        print(img[temp_z][temp_y][temp_x])
        if(img[temp_z][temp_y][temp_x] == 255):
            GS_sample_count = GS_sample_count + 1
    if (float(GS_sample_count) / temp_swcFiber.l > percent_tho):
        return True
    else:
        return  False


def FiberListGSCheck(swcFiber_list, swcPoint_list, img):
    GS_fiber = []
    NGS_fiber = []
    for temp_swcFiber in swcFiber_list:
        if(temp_swcFiber.fn == 0):
            continue
        if(FiberGSCheck(temp_swcFiber, swcPoint_list, img)):
            GS_fiber.append(temp_swcFiber)
        else:
            NGS_fiber.append(temp_swcFiber)

    test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//GSfiber.swc"
    for temp_swcFiber in GS_fiber:
        temp_swcFiber.Writeswc(test_filepath, swcPoint_list)
    test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//NGSfiber.swc"
    for temp_swcFiber in NGS_fiber:
        temp_swcFiber.Writeswc(test_filepath, swcPoint_list)


if __name__ == '__main__':
    # home_path = 'C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//neutube_ws2//raw//'
    home_path = "E://KaifengChen//neuTube_plus//dataset//result//256//segments//"
    test_path = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//"
    tiffGS_path = "E://KaifengChen//neuTube_plus//dataset//swc//256//tiff//"
    swcGS_path = "E://KaifengChen//neuTube_plus//dataset//swc//256//raw//"

    processed_num = 0
    for filepath, dirnames, filenames in os.walk(home_path):
        for filename in filenames:
            if(".swc" not in filename):
                continue
            file_AbsolutePath = os.path.join(filepath, filename)
            print("Processing file %s ..." %(file_AbsolutePath))

            swcPoint_list = Readswc(os.path.join(filepath, filename))
            swcFiber_list = BuildFiberList(swcPoint_list)

            img = io.imread(tiffGS_path + filename[0:-13] + "_produced.tif")
            # test_tholist = [5, 10, 15, 20]
            # for test_tho in test_tholist:
            #     if(not os.path.exists(test_path + "disttho=%d//"%(test_tho))):
            #         os.makedirs(test_path + "disttho=%d//"%(test_tho))
            #     KeyStructureFinder(swcFiber_list, swcPoint_list, "disttho=%d//"%(test_tho) + filename, test_tho)

            # FiberListGSCheck(swcFiber_list, swcPoint_list, img)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files had been processed!\n")