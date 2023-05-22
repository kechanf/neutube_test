import time
import random

from swc_tool_lib import *


debug_mode = 0

def ConnectGraph(graph, pA, pB, lenth):
    # print(pA.n, pB.n)
    # print(graph.distances(pA.n, pB.n))
    if(graph.distances(pA.n, pB.n)[0][0] > lenth):
        graph.add_edges([(pA.n, pB.n)])
    return graph

def WriteGraph(graph, swcPoint_list, save_path):
    waitlist = queue.Queue()
    for pA in swcPoint_list:
        swcPoint_list[pA.n].visited = 0
    for p in swcPoint_list:
        if(p.n == 0):continue
        if(swcPoint_list[p.n].visited):continue
        p.p = 0
        waitlist.put(p)
        while(True):
            if(waitlist.empty()):break
            pA = waitlist.get()
            swcPoint_list[pA.n].visited = 1
            pA.Writeswc(save_path, swcPoint_list)
            neig_list = graph.neighbors(pA.n)
            # print(f"neiglist = {neig_list}")
            for tenp_neig in neig_list:
                pB = swcPoint_list[tenp_neig]
                if(swcPoint_list[pB.n].visited):continue
                pB.p = pA.n
                waitlist.put(pB)

        # pA.p = 0
        # pA.Writeswc(filepath, swcPoint_list)
        # neiglist = graph.neighbors(pA.n)
        # print(f"neiglist = {neiglist}")
        # for(tenp_neig in neiglist):
        #     waitlist.put()

def BuildMSTGraph(swcPoint_list):
    MSTgraph = ig.Graph()
    MSTgraph.add_vertices(len(swcPoint_list))
    # print(len(swcPoint_list))
    MSTgraph.es['weight'] = []
    for p in swcPoint_list:
        for s in p.s:
            # print(p.n, s)
            MSTgraph.add_edges([(p.n, s)])
            weightlist = MSTgraph.es['weight']
            weightlist[len(weightlist) - 1] = 0.1
            MSTgraph.es['weight'] = weightlist
            # print(MSTgraph.es['weight'])
            # time.sleep(5)

    # time.sleep(100000)
    return MSTgraph

def ConnectWeightedGraph(graph, pA, pB, lenth, MSTgraph, weight):
    # print(pA.n, pB.n)
    # print(graph.distances(pA.n, pB.n))
    if(graph.distances(pA.n, pB.n)[0][0] > lenth):
        graph.add_edges([(pA.n, pB.n)])
        MSTgraph.add_edges([(pA.n, pB.n)])
        weightlist = MSTgraph.es['weight']
        weightlist[len(weightlist) - 1] = weight
        MSTgraph.es['weight'] = weightlist
        # print(MSTgraph.es['weight'])
    return graph, MSTgraph


def ConnTestV3(swcPoint_list, graph, GSswcPoint_list, GSgraph, save_path, MSTgraph, method, model):
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
        for SegB in FiberSeg_list:
            true_pA, true_pB, conn_flag, dist, angle, diff_r, diff_i = \
                CalcParmFiberSeg(SegA, SegB, swcPoint_list, GSswcPoint_list, GSgraph)
            test_X = [dist, angle, diff_r, diff_i]
            if(method == "svm"):
                test_X = [test_X]
                if(svm_model.predict(test_X)):
                    ConnectGraph(graph, true_pA, true_pB, len(swcPoint_list))
            elif(method == "nn"):
                X = torch.tensor([test_X]).to(torch.float32)
                y = model(X)
                # print(y)
                y[0] = 1 - float(y[0])
                if(y[0] < 0.6):
                    ConnectWeightedGraph(graph, true_pA, true_pB, len(swcPoint_list), MSTgraph, 1 + y[0])
            elif(method == "hist"):
                y = model.CalcScore(test_X)
                ConnectWeightedGraph(graph, true_pA, true_pB, len(swcPoint_list), MSTgraph, y)
                # if (y[0][0] < y[0][1]):
                #     ConnectGraph(graph, true_pA, true_pB, len(swcPoint_list))
                # pass
            elif(method == "GS"):
                if(conn_flag):
                    ConnectWeightedGraph(graph, true_pA, true_pB, len(swcPoint_list), MSTgraph, 0.1)
                    print(true_pA.n, true_pB.n, str(angle / 6.28 * 360), diff_r, diff_i)
                    for pp in SegA.p:
                        print(pp.n, pp.r, pp.i)
                    print("\n")
                    for pp in SegB.p:
                        print(pp.n, pp.r, pp.i)
                    print("\n")
            # if(conn_flag):
            #     parm_list.append([1, dist, angle, diff_r, diff_i])
            #     temp_count = temp_count + 1
            # else:
            #     parm_list.append([0, dist, angle, diff_r, diff_i])
    # print(temp_count)
    # print(MSTgraph.es['weight'])
    resgraph = MSTgraph.spanning_tree(weights = MSTgraph.es['weight'], return_tree = True)
    WriteGraph(resgraph, swcPoint_list, save_path)

if __name__ == '__main__':
    processed_num = 0
    parm_list = []
    avg_recall = 0
    avg_acc = 0

    method = "hist"
    if (method == "svm"):
        model = joblib.load(svm_model_path)
    elif (method == "nn"):
        model = ConnNet()
        model.load_state_dict(torch.load(nn_model_path))
        model.eval()
        # model = torch.load(nn_model_path)
    elif (method == "hist"):
        model = Conn_hist()
    elif (method == "GS"):
        model = []

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
            graph = BuildGraph(swcPoint_list)
            GSswcPoint_list = Readswc(GS_file_path)
            GSgraph = BuildGSGraph(GSswcPoint_list)

            swcPoint_list, GSswcPoint_list = UpdateMatchPointR(swcPoint_list, GSswcPoint_list)
            swcPoint_list, GSswcPoint_list = RecheckMatchPoint(swcPoint_list, GSswcPoint_list)

            swcPoint_list = UpdateListswcNeighborR(swcPoint_list)

            print(conn_res_path + filename[0:-13] + "_result.swc")
            MSTgraph = BuildMSTGraph(swcPoint_list)

            ConnTestV3(swcPoint_list, graph, GSswcPoint_list, GSgraph,
                       conn_res_path + filename[0:-13] + "_result.swc",
                       MSTgraph, "GS", model)


            # parm_list = CalcParmListV2(swcPoint_list, GSswcPoint_list, GSgraph, parm_list)
            # scaler = MinMaxScaler()
            # # parm_list = scaler.fit_transform(parm_list)
            # parm_list = np.asarray(parm_list)
            # svm_model = joblib.load(svm_model_path)
            # TPFN, TP, acc = 0, 0, 0
            # for line in parm_list:
            #     test_y, test_X = line[0], line[1:].reshape(1, -1)
            #     # print(test_y, test_X)
            #     if(test_y == 1):
            #         TPFN = TPFN + 1
            #         # print(svm_model.predict(test_X))
            #         if(svm_model.predict(test_X) == 1):
            #             TP = TP + 1
            #     if(svm_model.predict(test_X) == test_y):
            #         acc = acc + 1
            # if(TPFN == 0):
            #     TPFN = 1
            # print(f"recall = {(TP / TPFN * 100):>0.1f}%, acc = {(acc / len(parm_list) * 100):>0.1f}%")
            # avg_recall = avg_recall + TP / TPFN
            # avg_acc = avg_acc + acc / len(parm_list)
            # parm_list = []


            # swcPoint_list, swcFiber_list = ConnTestv2(swcPoint_list, GSgraph)
            # temp_path = conn_res_path + filename[0:-4] + "_conn_res.swc"
            # for f in swcFiber_list:
            #     if (f.fn == 0): continue
            #     f.Writeswc(temp_path, swcPoint_list)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files done!")

    # print(f"avg_recall = {(avg_recall / processed_num * 100):>0.1f}%, avg_acc = {(avg_acc / processed_num * 100):>0.1f}%")
