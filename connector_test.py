from swc_tool_lib import *

debug_mode = 0

def ConnTest(swcPoint_list, swcFiber_list):
    model = ConnNet()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    conn_p_count = 0

    for p in swcPoint_list:
        if(p.n == 0): continue
        for neig in p.neighbor:
            neig_p = swcPoint_list[neig[0]]
            if(neig_p.fn == p.fn): continue
            if(neig_p.fn in swcFiber_list[p.fn].connf): continue
            dist, angle = CalcConnParamPoint(p, neig_p, swcPoint_list)
            X = torch.tensor([dist, angle]).to(torch.float32)
            y = model(X)
            # print(y)
            if(y[0] < y[1]):
                conn_p_count = conn_p_count + 1
                if(p.EndCheck() == False and neig_p.EndCheck() == False): continue
                conn_p_count = conn_p_count + 1
                swcFiber_list[p.fn].connf.append(neig_p.fn)
                swcFiber_list[neig_p.fn].connf.append(p.fn)
                ConnFiber(swcPoint_list, swcFiber_list, p, neig_p)
    print(f"{conn_p_count} place have been connected!")
    return swcPoint_list, swcFiber_list


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

            swcPoint_list = UpdateListNeighbor(swcPoint_list)

            swcPoint_list, swcFiber_list = ConnTest(swcPoint_list, swcFiber_list)
            temp_path = conn_res_path + filename[0:-4] + "_conn_res.swc"
            for f in swcFiber_list:
                if (f.fn == 0): continue
                f.Writeswc(temp_path, swcPoint_list)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files done!")