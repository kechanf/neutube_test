import math
import time

from swc_tool_lib import *

class Conn_hist:
    def __init__(self):
        self.bins = 100
        self.feature = 4
        self.maxl = [0 for i in range(self.feature)]
        self.minl = [0 for i in range(self.feature)]
        self.step = [0 for i in range(self.feature)]
        self.hist = [[] for i in range(self.feature)]
        self.data = [[] for i in range(self.feature)]

        ConnParam_path = 'D://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx'
        df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
        df_data = np.asarray(df_data[1:])
        # flag = False
        for line in df_data:
            # print(line)
            if (line[0] == 0): continue
            for i in range(self.feature):
                # if(flag == False):self.data.append([line[i + 1]])
                # else:self.data[i].append(float(line[i + 1]))
                self.data[i].append(float(line[i + 1]))
            # flag = True
        # print(self.data)
        # time.sleep(1000)

        for i in range(self.feature):
            self.maxl[i] = max(self.data[i])
            self.minl[i] = min(self.data[i])
            self.step[i] = (self.maxl[i] - self.minl[i]) / self.bins
            self.hist[i] = self.myhist(self.data[i], self.bins)

    def CalcScore(self, X):
        score = 0
        for i in range(self.feature):
            # print(f"pro: {self.hist[i][math.floor((X[i] - self.minl[i]) / self.step[i])]}")
            # print(f"score: {score}")
            count = math.floor((X[i] - self.minl[i]) / self.step[i])
            if(count < 0):count = 0
            if(count >= self.feature):count = self.feature - 1
            score = score - math.log2(0.001 + self.hist[i][count])
        return score
    def myhist(self, templist, bins):
        maxl = max(templist)
        minl = min(templist)
        step = (maxl - minl) / (bins - 1)
        return_list = [0 for i in range(bins)]
        templist.sort()
        # print(templist)
        # time.sleep(100)
        count = 0
        # lower_p = minl
        # upper_p = minl + step
        for i in templist:
            # print(return_list)
            while(True):
                # print(minl + count * step)
                # print(i)
                # print(count)
                if(i >= minl + count * step and i < minl + (count + 1) * step):
                    break
                count = count + 1
            return_list[count] = return_list[count] + 1
        # print(return_list)
        for i in range(len(return_list)):
            return_list[i] = return_list[i] / len(templist)
        # print(return_list)
        return return_list

# conn_hist = Conn_hist()
#
# ConnParam_path = 'D://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx'
# conn_list = []
# unconn_list = []
# df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
# df_data = np.asarray(df_data[1:100])
# for line in df_data:
#     # print(line)
#     # print(conn_hist.CalcScore(line[1:]))
#     score = conn_hist.CalcScore(line[1:])
#     if(line[0] == 0):unconn_list.append(score)
#     else: conn_list.append(score)
    # print("\n")
# # print(conn_hist.CalcScore([6.740447896, 0.631352784, 0.302191707, 0.054901961]))
# # print("\n")
# # print(conn_hist.CalcScore([14.37055564, 1.400326767, 0.328712471, 0.274509804]))
# # print("\n")
# # 1 6.740447896, 0.631352784, 0.302191707, 0.054901961
# # 0 14.37055564, 1.400326767, 0.328712471, 0.274509804
# print(sum(conn_list) / len(conn_list))
# print(sum(unconn_list) / len(unconn_list))



def CalcHist():
    ConnParam_path = 'D://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx'
    df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
    df_data = np.asarray(df_data[1:])

    plot_list = []
    dist_list = []
    angle_list = []
    diff_i_list = []
    diff_r_list = []

    for line in df_data:
        # print(line)
        if(line[0] == 0):continue
        # time.sleep(1)
        dist, angle, diff_r, diff_i = float(line[1]), float(line[2]), float(line[3]), float(line[4])
        f = dist
        dist_list.append(dist)
        angle_list.append(angle)
        diff_i_list.append(diff_i)
        diff_r_list.append(diff_r)
        plot_list.append(f)

    def myhist(templist, bins = 100):
        maxl = max(templist)
        minl = min(templist)
        step = (maxl - minl) / (bins - 1)
        return_list = [0 for i in range(bins)]
        templist.sort()
        # print(templist)
        # time.sleep(100)
        count = 0
        # lower_p = minl
        # upper_p = minl + step
        for i in templist:
            # print(return_list)
            while(True):
                # print(minl + count * step)
                # print(i)
                # print(count)
                if(i >= minl + count * step and i < minl + (count + 1) * step):
                    break
                count = count + 1
            return_list[count] = return_list[count] + 1
        # print(return_list)
        for i in range(len(return_list)):
            return_list[i] = return_list[i] / len(templist)
        print(return_list)
        # return return_list



# ax1 = plt.subplot(321)
# ax1.bar(range(100), myhist(dist_list),
#         alpha = 0.5, color='r', label="dist")

# plt.xlabel('f')
# plt.ylabel('p')
# maxd = max(dist_list)
# mind = min(dist_list)
# maxa = max(angle_list)
# mina = min(angle_list)
# maxi = max(diff_i_list)
# mini = min(diff_i_list)
# maxr = max(diff_r_list)
# minr = min(diff_r_list)
# for i in range(len(dist_list)):
#     angle_list[i] = angle_list[i] / (maxa - mina) * (maxd - mind)
#     diff_i_list[i] = diff_i_list[i] / (maxi - mini) * (maxd - mind)
#     diff_r_list[i] = diff_r_list[i] / (maxr - minr) * (maxd - mind)
# plt.scatter(plot_list, [i for i in range(len(plot_list))], c="r")
# plt.hist(plot_list, density = True, bins = 100, alpha = 0.5, color='r')

    ax1 = plt.subplot(321)
    ax1.hist(dist_list, density = True, bins = 100, alpha = 0.5, color='r', label="dist")
    ax1.legend(loc='upper right')


    ax2 = plt.subplot(322)
    ax2.hist(angle_list, density = True, bins = 100, alpha = 0.5, color='b', label = "angle")
    ax2.legend(loc='upper right')


    ax3 = plt.subplot(323)
    ax3.hist(diff_i_list, density = True, bins = 100, alpha = 0.5, color='g', label="diff_i")
    ax3.legend(loc='upper right')


    ax4 = plt.subplot(324)
    ax4.hist(diff_r_list, density = True, bins = 100, alpha = 0.5, color='y', label="diff_r")
    ax4.legend(loc='upper right')

    # ax5 = plt.subplot(325)
    # ax5.hist(plot_list, density = True, bins = 100, alpha = 0.5, color='c', label="f")
    # ax5.legend(loc='upper right')


    # plt.ylim(0,0.5)
    plt.legend()
    plt.show()


# CalcHist()