"""
场景：一批swc文件，希望测出opt评分。该代码用于更改swc的格式，以适用于opt运行。
"""
import numpy as np
import random, glob, os
from swc_tool_lib import *


def parse_swc(swc_file):
    tree = []
    with open(swc_file) as fp:
        fp.readline()  # skip the header line 跳过标题行
        # 如果首字符是# ，跳过
        for line in fp.readlines():
            if line[0] == '#': continue
            line = line.strip()  # 去掉每行头尾的空白
            if not line: continue
            idx, type_, x, y, z, r, p = line.split()[0:7]
            idx = int(idx)
            type_ = int(type_)
            x = float(x)
            y = float(y)
            z = float(z)
            r = float(r)
            p = int(p)
            tree.append([idx, type_, x, y, z, r, p])
    return tree


def main():
    gt_dir = conn_res_path # rf'F:\seu_allen\additional_brains2\neu_smartTrace_brains2_exp040\smartTrace'  # 输入文件
    out_dir = opt_scoring_path # rf'F:\seu_allen\additional_brains2\neu_smartTrace_brains2_exp040\opt_smart'

    for filepath in glob.glob(os.path.join(gt_dir, '*.swc')):  # 读所有的swc文件
        fname = os.path.splitext(os.path.split(filepath)[-1])[0]
        print(fname)
        # input()
        out_swc_name = fname + ".swc"
        newfilepath = os.path.join(out_dir, out_swc_name)
        # print(fname)

        # 取坐标和父子连接信息
        tree = parse_swc(filepath)
        # print(rf'tree:{tree},{len(tree)}')
        if len(tree) == 0:
            continue
        pos = []
        c_p = []
        for point in tree:
            pos.append([point[2], point[3], point[4]])
            c_p.append([point[0], point[-1]])

        # # 原来
        # f = open(filepath, 'r', encoding='utf-8')
        # pos = []
        # c_p = []
        # for line in f:
        #     # 去除首位空格
        #     line = line.strip()
        #     # 去掉开头行
        #     if line[0] != '#':
        #         lsp = line.split(' ')
        #         n, _type, x, y, z, r, parent = lsp[0:7]
        #         # pos = " ".join([str(x), str(y), str(z)])
        #         # print(pos)
        #         pos.append([float(x), float(y), float(z)])  # 所有坐标以列表的方式存在swc里
        #         c_p.append([int(n), int(parent)])  # 所有父子关系存在c_p里

        # 更换父子信息序列号
        c_p_arr = np.array(c_p)
        # print(rf'c_p_arr:{c_p_arr}')
        newidx = np.arange(0, len(c_p_arr), 1)
        oldpid = c_p_arr[:, 1]
        # print(rf'oldpid:{oldpid}')
        # input()
        # input()
        newpid = []  # 新父节点
        mapdict = {}  # 映射关系
        for i, c_p1 in enumerate(c_p_arr):
            id = c_p1[0]  # n
            mapdict[id] = i  # 索引序列
        for pid in oldpid:
            if pid == -1 or pid not in c_p_arr[:, 0]:
                newpid.append(-1)
            else:
                newpid.append(mapdict[pid])
        newc_p = c_p_arr.copy()
        newc_p[:, 0] = newidx
        newc_p[:, 1] = newpid  # 新序列的父子关系

        # 把父子信息颠倒写两次
        xia = []
        b = []
        for c_p2 in newc_p:
            if c_p2[1] not in newidx:
                continue
            c, p = c_p2
            a = c, p
            b = p, c
            xia.append(a)
            xia.append(b)

        # 把坐标和父子信息更换为字符串类型并写入文件
        output = open(newfilepath, "w")
        for i in range(len(pos)):
            for j in range(len(pos[i])):
                output.write(str(pos[i][j]))
                output.write(' ')
            output.write('\n')
        output.write('\n')
        output.close()
        output = open(newfilepath, "a")
        for i in range(len(xia)):
            for j in range(len(xia[i])):
                output.write(str(xia[i][j]))
                output.write(' ')
            output.write('\n')
        output.close()


if __name__ == '__main__':
    main()
