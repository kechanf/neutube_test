import time

from swc_tool_lib import *

save_result = True

def FindMatchPointInGS(swcPoint_list, GSswcPoint_list, dist_tho=5):
    for p in swcPoint_list:
        if (p.n == 0): continue
        for GSp in GSswcPoint_list:
            if (GSp.n == 0): continue
            temp_dist = CalcswcPointDist(p, GSp)
            if (temp_dist < dist_tho):
                temp_cmpMP = swccmpPoint(GSp.n, temp_dist)
                if (not temp_cmpMP in p.swcMatchP):
                    p.swcMatchP.append(temp_cmpMP)
                temp_cmpMP = swccmpPoint(p.n, temp_dist)
                if (not temp_cmpMP in GSp.swcMatchP):
                    GSp.swcMatchP.append(temp_cmpMP)
            GSswcPoint_list[GSp.n] = GSp
        swcPoint_list[p.n] = p

    for p in swcPoint_list:
        if (p.swcMatchP): p.swcMatchP.sort()
        swcPoint_list[p.n] = p
    for p in GSswcPoint_list:
        if (p.swcMatchP): p.swcMatchP.sort()
        GSswcPoint_list[p.n] = p

    return swcPoint_list, GSswcPoint_list

def DistOnTreeTest(GSswcPoint_list, GSgraph):
    print(DistOnTree(GSswcPoint_list[1], GSswcPoint_list[2], GSgraph))
    print(DistOnTree(GSswcPoint_list[1], GSswcPoint_list[3], GSgraph))
    print(DistOnTree(GSswcPoint_list[1], GSswcPoint_list[4], GSgraph))


def CalcParmFiberSeg(SegA, SegB, swcPoint_list, GSswcPoint_list, GSgraph):
    iA, iB, rA, rB = 0, 0, 0, 0
    pA = SegA.p[0]
    mp_listB = []
    for p in SegB.p:
        for mp in p.mp:
            if (mp not in mp_listB):
                mp_listB.append(mp)
    conn_flag = False
    for mpA in pA.mp:
        if (conn_flag): break
        for mpB in mp_listB:
            if (conn_flag): break
            if (DistOnTree(GSswcPoint_list[mpA], GSswcPoint_list[mpB], GSgraph) == 1):
                conn_flag = True
    min_dist = CalcswcPointDist(pA, SegB.p[0])
    pB = SegB.p[0]
    for temp_pB in SegB.p:
        temp_dist = CalcswcPointDist(pA, temp_pB)
        if (temp_dist < min_dist):
            min_dist = temp_dist
            pB = temp_pB



    VectorA = [0, 0, 0]
    for p in SegA.p:
        VectorA = [VectorA[0] + p.x - pA.x,
                   VectorA[1] + p.y - pA.y,
                   VectorA[2] + p.z - pA.z]
    VectorB = [0, 0, 0]
    if (pB.EndCheck()):  # end to end
        # for p in SegB.p:
        #     VectorB = [VectorB[0] + p.x - pB.x,
        #                VectorB[1] + p.y - pB.y,
        #                VectorB[2] + p.z - pB.z]
        max_dist = 0
        for p in SegB.p:
            dis_temp = CalcswcPointDist(p, pB)
            if(max_dist < dis_temp):
                max_dist = dis_temp
                VectorB = [p.x - pB.x, p.y - pB.y, p.z - pB.z]

    else:  # end to mid
        # max_dist = CalcswcPointDist(pA, SegB.p[0])
        # far_pB = SegB.p[0]
        # for temp_pB in SegB.p:
        #     temp_dist = CalcswcPointDist(pA, temp_pB)
        #     if(temp_dist > max_dist):
        #         max_dist = temp_dist
        #         far_pB = temp_pB
        # for temp_pB in SegB.p:
        #     VectorB = [VectorB[0] + far_pB.x - temp_pB.x,
        #                VectorB[1] + far_pB.y - temp_pB.y,
        #                VectorB[2] + far_pB.z - temp_pB.z]
        VectorB = [swcPoint_list[pB.p].x - swcPoint_list[pB.s[0]].x,
                   swcPoint_list[pB.p].y - swcPoint_list[pB.s[0]].y,
                   swcPoint_list[pB.p].z - swcPoint_list[pB.s[0]].z]

    # time.sleep(3)
    # if(conn_flag):
    #     print(f"conn_flag = {conn_flag}, dist = {min_dist}, angle = {CalcVectorAngle(VectorA, VectorB)}, "
    #           f"diff_r = {abs(pA.r - pB.r)}, diff_i = {abs(pA.i - pB.i)}, -----{min_dist / ((pA.r + pB.r))}")
    #     print(pA.n, pB.n)
    # max_r = 0
    # max_i = 0
    # for p in swcPoint_list:
    #     max_r = max(max_r, p.r)
    #     max_i = max(max_i, p.i)

    for ppA in SegA.p:
        iA = iA + ppA.i
        rA = rA + ppA.r
    iA = iA / len(SegA.p)
    rA = rA / len(SegA.p)

    for ppB in SegB.p:
        iB = iB + ppB.i
        rB = rB + ppB.r
    iB = iB / len(SegB.p)
    rB = rB / len(SegB.p)

    # return pA, pB, conn_flag, min_dist, CalcVectorAngle(VectorA, VectorB), \
    #        float(abs(pA.r - pB.r)) / max_r, float(abs(pA.i - pB.i)) / max_i
    return pA, pB, conn_flag, min_dist, CalcVectorAngle(VectorA, VectorB), \
           float(abs(rA - rB)), float(abs(iA - iB))


def CalcParmListV2(swcPoint_list, GSswcPoint_list, GSgraph, parm_list):
    temp_count = 0
    for p in swcPoint_list:
        if (p.n == 0): continue
        if (p.EndCheck() == False): continue
        if (not p.swcNeig): continue
        SegA = swcFiberSeg()
        SegA.p.append(p)
        if (p.istail):
            if (not p.p == -1):
                SegA.p.append(swcPoint_list[p.p])
                if (not swcPoint_list[p.p].p == -1):
                    SegA.p.append(swcPoint_list[swcPoint_list[p.p].p])
        if (p.ishead):
            if (p.s):
                SegA.p.append(swcPoint_list[p.s[0]])
                if (SegA.p[1].s):
                    SegA.p.append(swcPoint_list[SegA.p[1].s[0]])
        if (len(SegA.p) == 1): exit(47)

        fn_list = []
        f_p_list = []
        for neig in p.swcNeig:
            pB = swcPoint_list[neig.n]
            if (pB.fn in fn_list):
                f_p_list[fn_list.index(pB.fn)].append(pB)
            else:
                fn_list.append(pB.fn)
                f_p_list.append([pB])

        FiberSeg_list = []
        for p_list in f_p_list:
            SegB = swcFiberSeg()
            if (len(p_list) == 1):
                pB = p_list[0]
                SegB.p.append(pB)
                if (pB.istail):
                    if (not pB.p == -1):
                        SegB.p.append(swcPoint_list[pB.p])
                    else:
                        exit(47)
                elif (pB.ishead):
                    if (pB.s):
                        SegB.p.append(swcPoint_list[pB.s[0]])
                    else:
                        exit(47)
                else:
                    if (not pB.p == -1):
                        SegB.p.append(swcPoint_list[pB.p])
                    if (pB.s):
                        SegB.p.append(swcPoint_list[pB.s[0]])
            else:
                for f_p in p_list:
                    SegB.p.append(f_p)
            FiberSeg_list.append(SegB)
        record_switch = False
        for SegB in FiberSeg_list:
            truepa, truepb, conn_flag, dist, angle, diff_r, diff_i = CalcParmFiberSeg(SegA, SegB, swcPoint_list, GSswcPoint_list, GSgraph)
            if(conn_flag):
                record_switch = True
                break
        if(record_switch == False):continue

        for SegB in FiberSeg_list:
            truepa, truepb, conn_flag, dist, angle, diff_r, diff_i = CalcParmFiberSeg(SegA, SegB, swcPoint_list, GSswcPoint_list, GSgraph)
            if(conn_flag):
                parm_list.append([1, dist, angle, diff_r, diff_i])
                temp_count = temp_count + 1
            else:
                parm_list.append([0, dist, angle, diff_r, diff_i])
    # print(f"temp_count {temp_count}")
    return parm_list, temp_count


def BuildGSGraph(GSswcPoint_list):
    GSgraph = ig.Graph()
    GSgraph.add_vertices(len(GSswcPoint_list))
    for p in GSswcPoint_list:
        for s in p.s:
            # print(p.n, s)
            GSgraph.add_edges([(p.n, s)])

    return GSgraph

def BuildGraph(swcPoint_list):
    graph = ig.Graph()
    graph.add_vertices(len(swcPoint_list))
    # print(len(swcPoint_list))
    for p in swcPoint_list:
        for s in p.s:
            # print(p.n, s)
            graph.add_edges([(p.n, s)])

    return graph


def DistOnTree(sourceP, targetP, GSgraph):
    return GSgraph.distances(sourceP.n, targetP.n)[0][0]


def UpdateMatchPoint(swcPoint_list, GSswcPoint_list, dist_tho=5):
    for p in swcPoint_list:
        if (p.n == 0): continue
        for GSp in GSswcPoint_list:
            if (CalcswcPointDist(p, GSp) < dist_tho):
                if (GSp.n not in p.mp):
                    p.mp.append(GSp.n)
                if (p.n not in GSp.mp):
                    GSp.mp.append(p.n)
            GSswcPoint_list[GSp.n] = GSp
        swcPoint_list[p.n] = p
    return swcPoint_list, GSswcPoint_list

def UpdateMatchPointR(swcPoint_list, GSswcPoint_list):
    for p in swcPoint_list:
        if (p.n == 0): continue
        for GSp in GSswcPoint_list:
            if (CalcswcPointDist(p, GSp) < (p.r + GSp.r) * 1.2):
                if (GSp.n not in p.mp):
                    p.mp.append(GSp.n)
                if (p.n not in GSp.mp):
                    GSp.mp.append(p.n)
            GSswcPoint_list[GSp.n] = GSp
        swcPoint_list[p.n] = p
    return swcPoint_list, GSswcPoint_list


def RecheckMatchPoint(swcPoint_list, GSswcPoint_list):
    for GSp in GSswcPoint_list:
        if (len(GSp.mp) > 1):
            true_mp = GSp.mp[0]
            min_dist = CalcswcPointDist(GSp, swcPoint_list[true_mp])
            for p in GSp.mp:
                temp_dist = CalcswcPointDist(GSp, swcPoint_list[p])
                if (temp_dist < min_dist):
                    min_dist = temp_dist
                    true_mp = p
            temp_mp = GSp.mp.copy()
            for p in GSp.mp:
                if (p == true_mp): continue
                temp_mp.remove(p)
                swcPoint_list[p].mp.remove(GSp.n)
            GSp.mp = temp_mp
            GSswcPoint_list[GSp.n] = GSp
    return swcPoint_list, GSswcPoint_list


def CheckBlockRange(x, y, z):
    x, y, z = round(x), round(y), round(z)
    if (x >= block_limit[0]): x = block_limit[0] - 1
    if (y >= block_limit[1]): y = block_limit[1] - 1
    if (z >= block_limit[2]): z = block_limit[2] - 1
    if (x < 0): x = 0
    if (y < 0): y = 0
    if (z < 0): z = 0
    return x, y, z


def UpdatePointIntensity(swcPoint_list, img):
    for p in swcPoint_list:
        if (p.n == 0): continue
        x, y, z = CheckBlockRange(p.x, p.y, p.z)
        # print(x, y, z)
        p.i = int(img[z][y][x])
        swcPoint_list[p.n] = p
    return swcPoint_list


if __name__ == '__main__':
    processed_num = 0
    parm_list = []
    for filepath, dirnames, filenames in os.walk(home_path):
        for filename in filenames:
            if (".swc" not in filename):
                continue
            GS_file_path = swcGS_path + filename[0:-13] + ".swc"
            if (not os.path.exists(GS_file_path)):
                print("no GS for %s" % (filename))
                continue
            tiff_file_path = tiff_path + filename[0:-13] + ".tif"
            if (not os.path.exists(tiff_file_path)):
                print("no TIFF for %s" % (filename))
                print(tiff_file_path)
                continue

            file_AbsolutePath = os.path.join(filepath, filename)
            print("Processing file %s ..." % (file_AbsolutePath))

            swcPoint_list = Readswc(os.path.join(filepath, filename))
            swcFiber_list = BuildFiberList(swcPoint_list)
            swcPoint_list = UpdatePointIntensity(swcPoint_list, load_image(tiff_file_path, False))
            GSswcPoint_list = Readswc(GS_file_path)
            GSgraph = BuildGraph(GSswcPoint_list)


            swcPoint_list, GSswcPoint_list = UpdateMatchPointR(swcPoint_list, GSswcPoint_list)
            swcPoint_list, GSswcPoint_list = RecheckMatchPoint(swcPoint_list, GSswcPoint_list)


            # GSswcFiber_list = BuildFiberList(GSswcPoint_list)
            # GSswcPoint_list = UpdateConnFromFiberlist(GSswcPoint_list, GSswcFiber_list)
            # GSswcPoint_list = ClearSP(GSswcPoint_list)

            # test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//GScomplete.swc"
            # for FiberA in GSswcFiber_list:
            #     FiberA.Writeswc(test_filepath, GSswcPoint_list)

            # swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list = \
            #     MatchFibers(swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list)
            # swcPoint_list, GSswcPoint_list = Recheckmp(swcPoint_list, GSswcPoint_list)

            # GSswcPoint_list, GSswcFiber_list, swcFiber_list = \
            #     SimpleConnFiberList(GSswcPoint_list, GSswcFiber_list, swcPoint_list, swcFiber_list)

            # swcPoint_list = UpdateListNeighbor(swcPoint_list)
            swcPoint_list = UpdateListswcNeighborR(swcPoint_list)
            # DistOnTreeTest(GSswcPoint_list, GSgraph)

            parm_list, conn_count = CalcParmListV2(swcPoint_list, GSswcPoint_list, GSgraph, parm_list)
            print(f"{conn_count} places have been found")

            # conn_param_list, unconn_param_list = CalcConnParamForList(swcPoint_list, GSswcPoint_list,
            #                                                           conn_param_list, unconn_param_list,
            #                                                           swcFiber_list)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files done!\n")

    if (save_result):
        wb = Workbook()
        ws = wb.active

        ws['A1'] = 'connection_property'
        ws['B1'] = 'distance'
        ws['C1'] = 'angle'
        ws['D1'] = 'radius_difference'
        ws['E1'] = 'intensity_difference'
        for line in parm_list:
            ws.append(line)
        wb.save('E://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx')
        print("data saved!")
