from swc_tool_lib import *

debug_mode = 0
visualize_mode = False
save_result = True


def ConnNeighbor(swcPointA, swcPointD, swcPoint_list):
    if (debug_mode == 323):
        swcPointA.Printswc()
        swcPointD.Printswc()
        print("\n\n\n\n")

    if ([swcPointD.n, False] in swcPointA.neighbor):
        neighbor_indexA = swcPointA.neighbor.index([swcPointD.n, False])
        if (not neighbor_indexA == -1):
            swcPointA.neighbor[neighbor_indexA] = [swcPointD.n, True]
    if ([swcPointA.n, False] in swcPointD.neighbor):
        neighbor_indexD = swcPointD.neighbor.index([swcPointA.n, False])
        if (not neighbor_indexD == -1):
            swcPointD.neighbor[neighbor_indexD] = [swcPointA.n, True]

    if ([swcPointD.n, False] in swcPointA.neighbor and [swcPointA.n, False] in swcPointD.neighbor and
            neighbor_indexA == -1 and neighbor_indexD == -1):
        swcPointA.Printswc()
        swcPointD.Printswc()
        print(CalcswcPointDist(swcPointA, swcPointD))
        exit(323)
    swcPoint_list[swcPointA.n] = swcPointA
    swcPoint_list[swcPointD.n] = swcPointD

    return swcPoint_list


def CalcConnParamPoint(swcPointA, swcPointB, swcPoint_list):
    angle_list = []
    A_wait_list = []
    B_wait_list = []
    if (not swcPointA.p == -1):
        A_wait_list.append(swcPoint_list[swcPointA.p])
    if (len(swcPointA.s) == 1):
        A_wait_list.append(swcPoint_list[swcPointA.s[0]])
    if (not swcPointB.p == -1):
        B_wait_list.append(swcPoint_list[swcPointB.p])
    if (len(swcPointB.s) == 1):
        B_wait_list.append(swcPoint_list[swcPointB.s[0]])
    for awp in A_wait_list:
        for bwp in B_wait_list:
            try:
                angle_list.append(CalcVectorAngle(
                    [awp.x - swcPointA.x, awp.y - swcPointA.y, awp.z - swcPointA.z],
                    [bwp.x - swcPointB.x, bwp.y - swcPointB.y, bwp.z - swcPointB.z]
                ))
            except:
                print("!!!!!!!!!!!")
                awp.Printswc()
                swcPointA.Printswc()
                bwp.Printswc()
                swcPointB.Printswc()
                print([awp.x - swcPointA.x, awp.y - swcPointA.y, awp.z - swcPointA.z])
                print([bwp.x - swcPointB.x, bwp.y - swcPointB.y, bwp.z - swcPointB.z])
                exit(330)
                pass
    if (len(angle_list) == 0):
        print("CalcConnParamPoint wrong")
        # for p in A_wait_list:
        #     p.Printswc()
        # for p in B_wait_list:
        #     p.Printswc()
        exit(323)

    return CalcswcPointDist(swcPointA, swcPointB), np.mean(angle_list)


def RecheckNeighbor(swcPoint_list):
    for p in swcPoint_list:
        if(p.n == 0):continue
        conn_fiber_list = []
        conn_fiber_min_dist = []
        conn_fiber_min_point = []
        for neig in p.neighbor:
            if(neig[1] == True):
                neig_p = swcPoint_list[neig[0]]
                if(not neig_p.fn in conn_fiber_list):
                    conn_fiber_list.append(neig_p.fn)
                    conn_fiber_min_dist.append(CalcswcPointDist(p, neig_p))
                    conn_fiber_min_point.append(neig[0])
                else:
                    temp_index = conn_fiber_list.index(neig_p.fn)
                    temp_dist = CalcswcPointDist(p, neig_p)
                    if(temp_dist < conn_fiber_min_dist[temp_index]):
                        conn_fiber_min_dist[temp_index] = temp_dist
                        conn_fiber_min_point[temp_index] = neig[0]
        temp_neig = []
        # if(conn_fiber_list):
        #     # print(conn_fiber_list)
        #     # print(conn_fiber_min_point)
        #     print("_____________")
        #     print(p.neighbor)
        # else: continue
        for neig in p.neighbor:
            neig_p = swcPoint_list[neig[0]]
            if(not neig_p.fn in conn_fiber_list):
                temp_neig.append(neig)
            elif(neig[1] == False): # have other fiber point connected
                swcPoint_list[neig[0]].neighbor.remove([p.n, False])
            elif(neig[1] == True and neig[0] == conn_fiber_min_point[conn_fiber_list.index(neig_p.fn)]):
                temp_neig.append(neig)
            else:
                swcPoint_list[neig[0]].neighbor.remove([p.n, True])
        p.neighbor = temp_neig
        # print(p.neighbor)
        swcPoint_list[p.n] = p
    return swcPoint_list






def CalcConnParamForList(swcPoint_list, GSswcPoint_list, conn_param_list, unconn_param_list, swcFiber_list):
    for swcPointA in swcPoint_list:  # A in TR (trace result)
        if (swcPointA.n == 0): continue
        if (len(swcPointA.mp) == 0): continue
        mp_fiber = GSswcPoint_list[swcPointA.mp[0]].fn
        temp_flag = False
        for mp in swcPointA.mp:  # mp in GS (gold standard)
            if (not GSswcPoint_list[mp].fn == mp_fiber):
                temp_flag = True
                break
        if (temp_flag): continue  # match points belongs to different fibers

        for Amp in swcPointA.mp:
            swcPointB = GSswcPoint_list[Amp]  # B in GS
            if (len(swcPointB.conn) == 0): continue  #
            for conn in swcPointB.conn:  # C in GS
                swcPointC = GSswcPoint_list[conn]
                if (len(swcPointC.mp) == 0):
                    continue

                elif (len(swcPointC.mp) == 1):
                    swcPointD = swcPoint_list[swcPointC.mp[0]]  # D in TR
                    swcPoint_list = ConnNeighbor(swcPointA, swcPointD, swcPoint_list)

                elif (len(swcPointC.mp) > 1):
                    end_D = []  # if fiber end point in mp?
                    for Cmp in swcPointC.mp:
                        swcPointD = swcPoint_list[Cmp]
                        # if(swcPointD.isend):
                        if (swcPointD.ishead or swcPointD.istail):
                            end_D.append(swcPointD)
                    if (len(end_D) == 0):
                        swcPointD = swcPoint_list[swcPointC.mp[0]]
                        min_dist = CalcswcPointDist(swcPointC, swcPointD)
                        for Cmp in swcPointC.mp:
                            temp_swcPointD = swcPoint_list[Cmp]
                            temp_dist = CalcswcPointDist(temp_swcPointD, swcPointC)
                            if (temp_dist < min_dist):
                                min_dist = temp_dist
                                swcPointD = temp_swcPointD
                        swcPoint_list = ConnNeighbor(swcPointA, swcPointD, swcPoint_list)
                    elif (len(end_D) == 1):
                        swcPointD = end_D[0]
                        swcPoint_list = ConnNeighbor(swcPointA, swcPointD, swcPoint_list)
                    elif (len(end_D) > 1):
                        swcPointD = end_D[0]
                        min_dist = CalcswcPointDist(swcPointC, swcPointD)
                        for temp_swcPointD in end_D:
                            temp_dist = CalcswcPointDist(temp_swcPointD, swcPointC)
                            if (temp_dist < min_dist):
                                min_dist = temp_dist
                                swcPointD = temp_swcPointD
                        swcPoint_list = ConnNeighbor(swcPointA, swcPointD, swcPoint_list)

    swcPoint_list = RecheckNeighbor(swcPoint_list)
    # conn_param_list = []
    # unconn_param_list = []
    conn_test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//conn"
    unconn_test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//unconn"
    conn_test_file_count = 0
    unconn_test_file_count = 0
    visual_test_path = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//visual_test"
    visual_count = 0
    for swcPointA in swcPoint_list:
        if (debug_mode == 330):
            pass
            # visual_count = visual_count + 1
            # temp_path = visual_test_path + str(visual_count) + ".swc"
            # for f in swcFiber_list:
            #     if(f.fn == 0):continue
            #     f.Writeswc(temp_path, swcPoint_list)
            #     # f.Printswc()
        if (len(swcPointA.neighbor) == 0): continue
        conn_flag = False
        for neighbor in swcPointA.neighbor:
            if (swcPoint_list[neighbor[1]]):
                conn_flag = True
                break
        if (conn_flag == False):
            continue
        for neighbor in swcPointA.neighbor:
            neighbotPoint = swcPoint_list[neighbor[0]]
            # Ensure that a pair of connections is counted only once when statistics
            if (neighbotPoint.n <= swcPointA.n): continue

            temp_dist, temp_angle = CalcConnParamPoint(swcPointA, neighbotPoint, swcPoint_list)
            if (neighbor[1] == True):
                if (conn_param_list):
                    conn_param_list[0].append(temp_dist)
                    conn_param_list[1].append(temp_angle)
                else:
                    conn_param_list.append([temp_dist])
                    conn_param_list.append([temp_angle])
                if (debug_mode == 327 and temp_dist > 5):
                    conn_test_file_count = conn_test_file_count + 1
                    temp_filepath = conn_test_filepath + "_num_%d_dist_%f_angle_%f.swc" \
                                    % (conn_test_file_count, temp_dist, temp_angle)
                    temp_fiber = swcFiber_list[swcPointA.fn]
                    temp_fiber.Writeswc(temp_filepath, swcPoint_list)
                    temp_fiber = swcFiber_list[swcPoint_list[neighbor[0]].fn]
                    temp_fiber.Writeswc(temp_filepath, swcPoint_list)
                if (debug_mode == 330):
                    visual_count = visual_count + 1
                    print("file%d" % (visual_count))
                    swcPointA.Printswc()
                    neighbotPoint.Printswc()
                    print("--------------------")
                    swcPoint_list, swcFiber_list = ConnFiber(swcPoint_list, swcFiber_list, neighbotPoint, swcPointA)
                    temp_path = visual_test_path + str(visual_count) + ".swc"
                    for f in swcFiber_list:
                        if (f.fn == 0): continue
                        f.Writeswc(temp_path, swcPoint_list)

            else:
                if (unconn_param_list):
                    unconn_param_list[0].append(temp_dist)
                    unconn_param_list[1].append(temp_angle)
                else:
                    unconn_param_list.append([temp_dist])
                    unconn_param_list.append([temp_angle])
                if (debug_mode == 327 and temp_dist < 2):
                    unconn_test_file_count = unconn_test_file_count + 1
                    temp_filepath = unconn_test_filepath + "_num_%d_dist_%f_angle_%f.swc" \
                                    % (unconn_test_file_count, temp_dist, temp_angle)
                    temp_fiber = swcFiber_list[swcPointA.fn]
                    temp_fiber.Writeswc(temp_filepath, swcPoint_list)
                    temp_fiber = swcFiber_list[swcPoint_list[neighbor[0]].fn]
                    temp_fiber.Writeswc(temp_filepath, swcPoint_list)

    if (debug_mode == 330):
        for f in swcFiber_list:
            if (f.fn == 0): continue
            f.Writeswc(visual_test_path + ".swc", swcPoint_list)
            # f.Printswc()

    return conn_param_list, unconn_param_list


if __name__ == '__main__':
    processed_num = 0
    conn_param_list = []
    unconn_param_list = []
    for filepath, dirnames, filenames in os.walk(home_path):
        for filename in filenames:
            if (".swc" not in filename):
                continue
            GS_file_path = swcGS_path + filename[0:-13] + ".swc"
            if (not os.path.exists(GS_file_path)):
                print("no GS for %s" % (filename))
                continue

            file_AbsolutePath = os.path.join(filepath, filename)
            print("Processing file %s ..." % (file_AbsolutePath))

            swcPoint_list = Readswc(os.path.join(filepath, filename))
            swcFiber_list = BuildFiberList(swcPoint_list)
            GSswcPoint_list = Readswc(GS_file_path)
            GSswcFiber_list = BuildFiberList(GSswcPoint_list)
            GSswcPoint_list = UpdateConnFromFiberlist(GSswcPoint_list, GSswcFiber_list)
            GSswcPoint_list = ClearSP(GSswcPoint_list)

            # test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//GScomplete.swc"
            # for FiberA in GSswcFiber_list:
            #     FiberA.Writeswc(test_filepath, GSswcPoint_list)

            swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list = \
                MatchFibers(swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list)
            swcPoint_list, GSswcPoint_list = Recheckmp(swcPoint_list, GSswcPoint_list)

            # GSswcPoint_list, GSswcFiber_list, swcFiber_list = \
            #     SimpleConnFiberList(GSswcPoint_list, GSswcFiber_list, swcPoint_list, swcFiber_list)

            swcPoint_list = UpdateListNeighbor(swcPoint_list)
            conn_param_list, unconn_param_list = CalcConnParamForList(swcPoint_list, GSswcPoint_list,
                                                                      conn_param_list, unconn_param_list,
                                                                      swcFiber_list)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files done!")

    # visualize
    if (visualize_mode):
        plt.xlabel('dist')
        plt.ylabel('angle')
        plt.scatter(unconn_param_list[0], unconn_param_list[1], c="r", label="unconnected")
        plt.scatter(conn_param_list[0], conn_param_list[1], c="b", label='connected')
        plt.legend()
        plt.show()
    if (save_result):
        wb = Workbook()
        ws = wb.active

        ws['A1'] = 'connection_property'
        ws['B1'] = 'distance'
        ws['C1'].value = 'angle'
        for i in range(0, len(conn_param_list[0])):
            ws.append([1, conn_param_list[0][i], conn_param_list[1][i]])
        for i in range(0, len(unconn_param_list[0])):
            ws.append([0, unconn_param_list[0][i], unconn_param_list[1][i]])
        wb.save('E://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx')
        print("data saved!")
