from swc_tool_lib import *

debug_mode = 32302


def CompareFibers(FiberA, swcPoint_listA, swcFiber_listA,
                  FiberB, swcPoint_listB, swcFiber_listB,
                  dist_tho=10, match_rate=0.8):
    close_point_count = 0
    for spA in FiberA.sp:
        for spB in FiberB.sp:
            if (CalcswcPointDist(swcPoint_listA[spA], swcPoint_listB[spB]) < dist_tho):
                close_point_count = close_point_count + 1

    if (close_point_count / FiberA.l < match_rate):  # low match rate, no match on GS
        return swcPoint_listA, swcFiber_listA, swcPoint_listB, swcFiber_listB, False
    else:
        for spA in FiberA.sp:
            for spB in FiberB.sp:
                if (CalcswcPointDist(swcPoint_listA[spA], swcPoint_listB[spB]) < dist_tho):
                    if not spB in swcPoint_listA[spA].mp: swcPoint_listA[spA].mp.append(spB)
                    if not spA in swcPoint_listB[spB].mp: swcPoint_listB[spB].mp.append(spA)
        if not FiberB.fn in swcFiber_listA[FiberA.fn].mf: swcFiber_listA[FiberA.fn].mf.append(FiberB.fn)
        if not FiberA.fn in swcFiber_listB[FiberB.fn].mf: swcFiber_listB[FiberB.fn].mf.append(FiberA.fn)
        return swcPoint_listA, swcFiber_listA, swcPoint_listB, swcFiber_listB, True


def MatchFibers(swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list):
    for swcFiberA in swcFiber_list:
        if (swcFiberA.fn == 0): continue
        for swcFiberB in GSswcFiber_list:
            if (swcFiberB.fn == 0): continue
            swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list, res1 = \
                CompareFibers(swcFiberA, swcPoint_list, swcFiber_list,
                              swcFiberB, GSswcPoint_list, GSswcFiber_list)
            # swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list, res2 = \
            #     CompareFibers(swcFiberA, swcPoint_list, swcFiber_list,
            #                   swcFiberB, GSswcPoint_list, GSswcFiber_list)

    if (debug_mode == 320):
        fiber_match_count = 0
        GSfiber_match_count = 0
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetest.swc"
        for swcFiberA in swcFiber_list:
            if (len(swcFiberA.mf)):
                fiber_match_count = fiber_match_count + 1
                swcFiberA.Writeswc(test_filepath, swcPoint_list)
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetestGS.swc"
        for swcFiberA in GSswcFiber_list:
            if (len(swcFiberA.mf)):
                GSfiber_match_count = GSfiber_match_count + 1
                swcFiberA.Writeswc(test_filepath, GSswcPoint_list)
        print("%d result fibers matched to GS!" % (fiber_match_count))
        print("%d GS fibers matched to result!" % (GSfiber_match_count))

    if (debug_mode == 323):
        file_count = 0
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetest.swc"
        GStest_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetestGS.swc"
        for swcFiberA in GSswcFiber_list:
            if (swcFiberA.fn == 0): continue
            # file_count = file_count + 1
            # swcFiberA.Writeswc(GStest_filepath[0:-4] + str(file_count) + ".swc", GSswcPoint_list)
            if (len(swcFiberA.mf) >= 2):
                file_count = file_count + 1
                temp_test_filepath = test_filepath[0:-4] + str(file_count) + ".swc"
                temp_GStest_filepath = GStest_filepath[0:-4] + str(file_count) + ".swc"
                swcFiberA.Writeswc(temp_GStest_filepath, GSswcPoint_list)
                for mf in swcFiberA.mf:
                    swcFiberB = swcFiber_list[mf]
                    swcFiberB.Writeswc(temp_test_filepath, swcPoint_list)
        print("%d fiber in GS matches to fibers in TR!" % (file_count))

    if (debug_mode == 32302):
        file_count = 0
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetest.swc"
        GStest_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetest.swc"
        for swcFiberA in swcFiber_list:
            if (swcFiberA.fn == 0): continue
            # file_count = file_count + 1
            # swcFiberA.Writeswc(GStest_filepath[0:-4] + str(file_count) + ".swc", GSswcPoint_list)
            if (len(swcFiberA.mf) >= 2):
                file_count = file_count + 1
                temp_test_filepath = test_filepath[0:-4] + str(file_count) + ".swc"
                temp_GStest_filepath = GStest_filepath[0:-4] + str(file_count) + "GS.swc"
                swcFiberA.Writeswc(temp_test_filepath, swcPoint_list)
                for mf in swcFiberA.mf:
                    swcFiberB = GSswcFiber_list[mf]
                    swcFiberB.Writeswc(temp_GStest_filepath, GSswcPoint_list)
        print("%d fiber in GS matches to fibers in TR!" % (file_count))

    if (debug_mode == 3201):
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetest1.swc"
        GStest_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//comparetestGS1.swc"
        swcFiberA = swcFiber_list[5]
        if (len(swcFiberA.mf)):
            swcFiberA.Writeswc(test_filepath, swcPoint_list)
            for mf in swcFiberA.mf:
                GSswcFiber_list[mf].Writeswc(GStest_filepath, GSswcPoint_list)

    fiber_match_count = 0
    GSfiber_match_count = 0
    for swcFiberA in swcFiber_list:
        if (len(swcFiberA.mf)):
            fiber_match_count = fiber_match_count + 1
    for swcFiberA in GSswcFiber_list:
        if (len(swcFiberA.mf)):
            GSfiber_match_count = GSfiber_match_count + 1
    print("%d result fibers matched to GS!" % (fiber_match_count))
    print("%d GS fibers matched to result!" % (GSfiber_match_count))

    return swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list


def Recheckmp(swcPoint_list, GSswcPoint_list):
    for GSp in GSswcPoint_list:
        if (len(GSp.mp) >= 2):
            mp_check_list = []
            fn_list = []
            for mp in GSp.mp:
                if (not swcPoint_list[mp].fn in fn_list):
                    fn_list.append(swcPoint_list[mp].fn)
                    mp_check_list.append([mp])
                else:
                    mp_check_list[fn_list.index(swcPoint_list[mp].fn)].append(mp)
            # print(mp_check_list)
            for mp_line in mp_check_list:
                if (len(mp_line) == 1): continue
                min_dist = 100000
                min_mp = mp_line[0]
                for mp in mp_line:
                    temp_dist = CalcswcPointDist(GSp, swcPoint_list[mp])
                    if (temp_dist < min_dist):
                        min_dist = temp_dist
                        min_mp = mp
                for mp in mp_line:
                    if (mp == min_mp): continue
                    GSp.mp.remove(mp)
                    swcPoint_list[mp].mp.remove(GSp.n)

            GSswcPoint_list[GSp.n] = GSp

    return swcPoint_list, GSswcPoint_list


def SimpleConnFiberList(GSswcPoint_list, GSswcFiber_list, swcPoint_list, swcFiber_list):
    file_count = 0
    test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//margeFiber"
    for swcFiberA in swcFiber_list:
        if (len(swcFiberA.mf) >= 2):
            # for mf1 in swcFiberA.mf:
            #     for mf2 in swcFiberA.mf:
            #         res, GSswcPoint_list, GSswcFiber_list, swcFiber_list = \
            #             SimpleConnFiber(
            #                 GSswcFiber_list[mf1], GSswcFiber_list[mf2], GSswcPoint_list, GSswcFiber_list, swcFiber_list)
            if (debug_mode == 327):
                file_count = file_count + 1
                temp_path = test_filepath + "%d.swc" % (file_count)
                swcFiberA.Writeswc(temp_path, swcPoint_list)
                temp_path = test_filepath + "%dGS.swc" % (file_count)
                for mf in swcFiberA.mf:
                    GSswcFiber_list[mf].Writeswc(temp_path, GSswcPoint_list)

    return GSswcPoint_list, GSswcFiber_list, swcFiber_list


if __name__ == '__main__':
    processed_num = 0
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

            swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list = \
                MatchFibers(swcPoint_list, swcFiber_list, GSswcPoint_list, GSswcFiber_list)

            processed_num = processed_num + 1
