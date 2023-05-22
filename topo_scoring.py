import os.path
import time

from swc_tool_lib import *

start = time.time()
# num_false_set = [1, 5, 10, 15, 20, 25, 30, 35, 40]
# num_false_set = [3, 6, 9, 12]

save_path = topology_scoring_result # rf'F:\result\opt\three bifurcation\tb5_{num_false}_result.txt'  # 存放记录的文件
out_dir = conn_res_path #  origin_path # r'F:\data_newmetric\opt\gt_opt'
gt_dir = swcGS_path # rf'F:\data_newmetric\opt\three_bifurcation_5_opt\{num_false}'  # 金标准

# save_path = r'C:\Users\braintell\Desktop\result\opt\app2\app2_result.txt'  # 存放记录的文件
# gt_dir = r'C:\Users\braintell\Desktop\homework\D\seuproject\metric\swcdata\app2Manual_zy\opt\gt_opt'
# out_dir = r'C:\Users\braintell\Desktop\data_newmetric\opt\app2'
# print(len(glob.glob(os.path.join(gt_dir, '*.swc'))))

file_num = 0
optj_avg_precision, optj_avg_recall, optj_avg_f1 = 0, 0, 0
optp_avg_con_prob_precis, optp_avg_con_prob_recall, optp_avg_con_prob_f1 = 0, 0, 0
optg_avg_spurious, optg_avg_missings, optg_avg_f1 = 0, 0, 0

for G_gt_path in glob.glob(os.path.join(gt_dir, '*.swc')):  # 读所有的swc文件
    print(G_gt_path)
    num = os.path.splitext(os.path.split(G_gt_path)[-1])[0]
    # print(num)
    out_swc_name = num + "_result.swc"
    print(out_swc_name)

    G_pred_path = os.path.join(out_dir, out_swc_name)
    if(not os.path.exists(G_pred_path)):
        continue
    # print(G_gt_path)
    # print(G_pred_path)
    # time.sleep(10000)
    # print('fname的值为：{}'.format(num))

    start = time.time()

    ##r4096 = (-4096, -4096)
    r4096 = (-4096, -4096, -4096)
    SHIFTS = {
        "toronto": r4096,
        "la": r4096,
        "new york": r4096,
        ##"boston": (4096, -4096),
        "boston": (4096, -4096, -4096),
        ##"chicago": (-4096, -8192),
        "chicago": (-4096, -8192, -4096),
        "amsterdam": r4096,
        "denver": r4096,
        "kansas city": r4096,
        "montreal": r4096,
        "paris": r4096,
        "pittsburgh": r4096,
        "saltlakecity": r4096,
        "san diego": r4096,
        "tokyo": r4096,
        "vancouver": r4096,
        ##"columbus": (-4096, -8192),
        "columbus": (-4096, -8192, -4096),
        ##"minneapolis": (-4096, -8192),
        "minneapolis": (-4096, -8192, -4096),
        ##"nashville": (-4096, -8192)}
        "nashville": (-4096, -8192, -4096)}

    # print("loading the graphs")  # 加载图片
    G_gt = md.load_graph_swc(G_gt_path)
    G_pred = md.load_graph_swc(G_pred_path)
    # print(G_gt, G_pred)
    # time.sleep(10000)
    city = "vancouver"

    # --------------------------------------------------opt_j
    f1, precision, recall, \
    tp, pp, ap, \
    matches_g, matches_hg, \
    g_gt_snap, g_pred_snap = md.opt_j(G_gt,
                                      G_pred,
                                      th_existing=1,  # 在捕获过程中，只有当该边的所有端点都不在th_existing范围内时，才会将一个附加节点插入到该边中
                                      th_snap=25,  # 如果一个点到最近的边的距离小于th_snap，那么它就被折入图中
                                      alpha=100)  # 鼓励匹配具有相似顺序的两个节点

    optj_avg_precision = optj_avg_precision + precision
    optj_avg_recall = optj_avg_recall + recall
    optj_avg_f1 = optj_avg_f1 + f1
    with open(save_path, 'a') as f:  # 设置文件对象
        print(
            "OPT-J:          filename:{} precision={:0.3f} recall={:0.3f} f1={:0.3f}".format(num, precision,
                                                                                               recall,
                                                                                               f1), file=f)
    # print(
    #     "???????????OPT-J:          filename:{} precision={:0.3f} recall={:0.3f} f1={:0.3f}\n".format(num, precision,
    #                                                                                        recall, f1))

    # --------------------------------------------------
    # scale = 1/4
    # segments = np.array([[G_gt.nodes[s]['pos'], G_gt.nodes[t]['pos']] for s,t in G_gt.edges()])
    # gt_s = md.render_segments(segments*scale,
    #                           filename=None,
    #                           height=h*scale,
    #                           width=w*scale,
    #                           thickness=1)
    #
    # segments = np.array([[G_pred.nodes[s]['pos'], G_pred.nodes[t]['pos']] for s,t in G_pred.edges()])
    # pred_s = md.render_segments(segments*scale,
    #                             filename=None,
    #                             height=h*scale,
    #                             width=w*scale,
    #                             thickness=1)
    #
    # corr, comp, qual, TP_g, TP_p, FN, FP = md.corr_comp_qual(gt_s,
    #                                                          pred_s,
    #                                                          slack=8*scale)
    # print("Corr-Comp-Qual: corr={:0.3f} comp={:0.3f} qual={:0.3f}\n".format(corr, comp, qual))
    #
    # # --------------------------------------------------
    # correct, too_long, too_short, infeasible = md.toolong_tooshort(G_gt, G_pred,
    #                                                                n_paths=50, # to speed up this script
    #                                                                max_node_dist=25)
    # print("2Long-2Short:   correct={:0.3f} 2l+2s={:0.3f} inf={:0.3f}\n".format(correct, too_long+too_short, infeasible))

    # --------------------------------------------------
    n_conn_precis, n_conn_recall, \
    n_inter_precis, n_inter_recall, \
    con_prob_precis, con_prob_recall, con_prob_f1 = md.opt_p(G_gt, G_pred)

    optp_avg_con_prob_precis = optp_avg_con_prob_precis + con_prob_precis
    optp_avg_con_prob_recall = optp_avg_con_prob_recall + con_prob_recall
    optp_avg_con_prob_f1 = optp_avg_con_prob_f1 + con_prob_f1
    with open(save_path, 'a') as f:  # 设置文件对象
        print(
            "OPT-P:          filename:{} con_prob_precis={:0.3f} con_prob_recall={:0.3f} con_prob_f1={:0.3f}".format(
                num,
                con_prob_precis,
                con_prob_recall,
                con_prob_f1), file=f)
    # print(
    #     "OPT-P:          filename:{} con_prob_precis={:0.3f} con_prob_recall={:0.3f} con_prob_f1={:0.3f}\n".format(num,
    #                                                                                                                con_prob_precis,
    #                                                                                                                con_prob_recall,
    #                                                                                                                con_prob_f1))

    # --------------------------------------------------
    # f1, spurious, missings, \
    # n_preds_sum, n_gts_sum, \
    # n_spurious_marbless_sum, \
    # n_empty_holess_sum = md.holes_marbles(G_gt, G_pred,
    #                                       spacing=10,
    #                                       dist_limit=300,
    #                                       dist_matching=25,
    #                                       N=50,  # to speed up this script
    #                                       verbose=False)
    # print("Hole-Marbles:   spurious={:0.3f} missings={:0.3f} f1={:0.3f}\n".format(spurious, missings, f1))

    # --------------------------------------------------
    f1, spurious, missings, \
    n_preds_sum, n_gts_sum, \
    n_spurious_marbless_sum, \
    n_empty_holess_sum = md.opt_g(G_gt, G_pred,
                                  spacing=10,
                                  dist_limit=300,
                                  dist_matching=25,
                                  N=50,  # to speed up this script
                                  verbose=False)
    optg_avg_spurious = optg_avg_spurious + spurious
    optg_avg_missings = optg_avg_missings + missings
    optg_avg_f1 = optg_avg_f1 + f1
    with open(save_path, 'a') as f:  # 设置文件对象
        print("OPT-G:          filename:{} spurious={:0.3f} missings={:0.3f} f1={:0.3f}\n".format(num, spurious,
                                                                                                  missings,
                                                                                                  f1), file=f)
    file_num = file_num + 1
    print(f"{file_num} files done!\n")
    # print("OPT-G:          filename:{} spurious={:0.3f} missings={:0.3f} f1={:0.3f}\n".format(num, spurious, missings,
    #                                                                                           f1))

    # --------------------------------------------------
    # end = time.time()
    # print("循环运行时间:%f秒" % (end - start))
    # localtime = time.asctime(time.localtime(time.time()))
    # print("本地时间为：{}\n".format(localtime))
with open(save_path, 'a') as f:
    print("OPT-J: precision=      {:0.3f} recall=         {:0.3f} f1=         {:0.3f}".format(
        optj_avg_precision / file_num, optj_avg_recall / file_num, optj_avg_f1 / file_num))
    print("OPT-P: con_prob_precis={:0.3f} con_prob_recall={:0.3f} con_prob_f1={:0.3f}".format(
        optp_avg_con_prob_precis / file_num, optp_avg_con_prob_recall / file_num, optp_avg_con_prob_f1 / file_num))
    print("OPT-G: spurious=       {:0.3f} missings=       {:0.3f} f1=         {:0.3f}\n".format(
        optg_avg_spurious / file_num, optg_avg_missings / file_num, optg_avg_f1 / file_num))

print("OPT-J: precision=      {:0.3f} recall=         {:0.3f} f1=         {:0.3f}".format(
        optj_avg_precision / file_num, optj_avg_recall / file_num, optj_avg_f1 / file_num))
print("OPT-P: con_prob_precis={:0.3f} con_prob_recall={:0.3f} con_prob_f1={:0.3f}".format(
    optp_avg_con_prob_precis / file_num, optp_avg_con_prob_recall / file_num, optp_avg_con_prob_f1 / file_num))
print("OPT-G: spurious=       {:0.3f} missings=       {:0.3f} f1=         {:0.3f}\n".format(
    optg_avg_spurious / file_num, optg_avg_missings / file_num, optg_avg_f1 / file_num))