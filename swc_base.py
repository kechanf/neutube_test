import time

from swc_tool_lib import *

debug_mode = 0

class swcPoint:
    def __init__(self, sample_number, structure_identifier,
                 x_position, y_position, z_position, radius, parent_sample):
        self.n = sample_number
        self.si = structure_identifier
        self.x = x_position
        self.y = y_position
        self.z = z_position
        self.r = radius
        self.p = parent_sample
        self.s = [] # sons
        self.fn = -1 # fiber number
        self.conn = [] # connect points in other fiber
        self.mp = [] # match point in other swc
        self.neighbor = [] # neighbor closer than a distance. store neighbor number and connect info. as [d, bool]
        # self.isend = False
        self.ishead = False
        self.istail = False
        self.swcNeig = [] # neighbor closer than a distance.
        self.swcMatchP = []
        self.i = 0
        self.visited = 0

    def EndCheck(self):
        return self.ishead or self.istail


    def Printswc(self):
        print("n=%d, si=%d, x=%f, y=%f, z=%f, r=%f, p=%d, s=%s, fn=%d, neighbor=%s, mp=%s"
              %(self.n, self.si, self.x, self.y, self.z, self.r, self.p, str(self.s),
                self.fn, str(self.neighbor), str(self.mp)))

    def Writeswc(self, filepath, swcPoint_list,
                 reversal=False, limit=[256, 256, 128],
                 overlay=False, number_offset=0):
        if(reversal):
            line = "%d %d %f %f %f %f %d\n" %(
                self.n + number_offset, self.si, self.x,
                limit[1] - self.y,
                self.z, self.r, self.p + number_offset
            )
        else:
            line = "%d %d %f %f %f %f %d\n" %(
                self.n + number_offset, self.si, self.x,
                self.y,
                self.z, self.r, self.p + number_offset
            )
        if (overlay and os.path.exists(filepath)):
            # print("!!!!!!")
            os.remove(filepath)
        file_handle = open(filepath, mode="a")
        file_handle.writelines(line)
        file_handle.close()



class swccmpPoint:
    def __init__(self, number, dist):
        self.n = number
        self.dist = dist
        # self.angle = angle

    def __lt__(self, other):
        return self.dist < other.dist


    def Printswc(self):
        print(self.n, self.dist)

class swcFiberSeg:
    def __init__(self):
        self.p = []


class swcFiber:
    def __init__(self, fiber_number):
        self.l = 0
        self.fn = fiber_number
        self.sp = [] # points
        self.ep = [] # 0 for head and 1 for tail
        self.mf = [] # match fibers
        self.state = True
        self.connf = [] # connected fibers

    def Printswc(self):
        print("l=%d, fn=%d, sp=%s, ep=%s" %(self.l, self.fn, str(self.sp), str(self.ep)))

    def Writeswc(self, filepath, swcPoint_list,
                 reversal = False, limit = [256, 256, 128],
                 overlay = False, number_offset = 0):
        temp_swcPoint_list = []
        for temp_sp in self.sp:
            temp_swcPoint_list.append(swcPoint_list[temp_sp])
        Writeswc(filepath, temp_swcPoint_list, reversal, limit, overlay, number_offset)

    def HeadCheck(self, swcPoint_list, temp_swcPoint_number):
        if (swcPoint_list[temp_swcPoint_number].p == -1  # no parent
                or (not len(swcPoint_list[swcPoint_list[temp_swcPoint_number].p].s) == 1)):  # have brother
            return True
        else:
            return False


    def TailCheck(self, swcPoint_list, temp_swcPoint_number):
        if(not len(swcPoint_list[temp_swcPoint_number].s) == 1):
            return True
        else:
            return False

    # def EndCheck(self, swcPoint_list, temp_swcPoint_number):
    #     if(self.HeadCheck(swcPoint_list, temp_swcPoint_number) or self.TailCheck(swcPoint_list, temp_swcPoint_number)):
    #         return True
    #     else:
    #         return False


    def UpdateEnd(self, swcPoint_list):
        # print(swcPoint_list)
        self.ep = [0,0]
        for son_number in self.sp:
            # if(self.EndCheck(swcPoint_list, son_number)):
            #     self.ep.append(son_number)
            #     swcPoint_list[son_number].isend = True
            if(self.HeadCheck(swcPoint_list, son_number)):
                self.ep[0] = son_number
                swcPoint_list[son_number].ishead = True
            elif(self.TailCheck(swcPoint_list, son_number)):
                self.ep[1] = son_number
                swcPoint_list[son_number].istail = True

        if(debug_mode == 3):
            # if(not len(self.ep) == 2):
            self.Printswc()
        if(0 in self.ep):
            self.ep = []
        return swcPoint_list

    def UpdateConn(self, swcPoint_list):
        for temp_ep in self.ep:
            swcPointA = swcPoint_list[temp_ep]
            if(not swcPointA.p == -1):
                swcPointB = swcPoint_list[swcPointA.p]
                if (not swcPointB.fn == swcPointA.fn):
                    swcPoint_list = AddConn(swcPoint_list, swcPointA, swcPointB)
            if len(swcPointA.s):
                for temp_s in swcPointA.s:
                    swcPointB = swcPoint_list[temp_s]
                    if(not swcPointB.fn == swcPointA.fn):
                        swcPoint_list = AddConn(swcPoint_list, swcPointA, swcPointB)
        return swcPoint_list

def UpdateConnFromFiberlist(swcPoint_list, swcFiber_list):
    for swcFiberA in swcFiber_list:
        swcPoint_list = swcFiberA.UpdateConn(swcPoint_list)

    if(debug_mode == 320):
        swcFiberA = swcFiber_list[5]
        test_filepath = test_path + "conntest.swc"
        swcFiberA.Writeswc(test_filepath, swcPoint_list)
        for sp in swcFiberA.sp:
            if(not swcPoint_list[sp].conn):
                continue
            for conn in swcPoint_list[sp].conn:
                swcFiberB = swcFiber_list[swcPoint_list[conn].fn]
                swcFiberB.Writeswc(test_filepath, swcPoint_list)

    return swcPoint_list

def AddConn(swcPoint_list, swcPointA, swcPointB):
    if(not swcPointB.n in swcPointA.conn):
        swcPointA.conn.append(swcPointB.n)
    if(not swcPointA.n in swcPointB.conn):
        swcPointB.conn.append(swcPointA.n)
    swcPoint_list[swcPointA.n] = swcPointA
    swcPoint_list[swcPointB.n] = swcPointB
    return swcPoint_list

def Readswc(swc_name):
    with open(swc_name, 'r' ) as f:
        lines = f.readlines()

    swcPoint_number = -1
    swcPoint_list = []
    point_list = []
    list_map = np.zeros(500000)

    for line in lines:
        if(line[0] == '#'):
            continue

        temp_line = line.split()
        # print(temp_line)
        point_list.append(temp_line)

        swcPoint_number = swcPoint_number + 1
        list_map[int(temp_line[0])] = swcPoint_number

    # print(point_list)
    swcPoint_number = 0
    for point in point_list:
        swcPoint_number = swcPoint_number + 1
        point[0] = swcPoint_number # int(point[0])
        point[1] = int(point[1])
        point[2] = float(point[2])
        point[3] = float(point[3])
        point[4] = float(point[4])
        point[5] = float(point[5])
        point[6] = int(point[6])
        if(point[6] == -1):
            pass
        else:
            point[6] = int(list_map[int(point[6])]) + 1

    swcPoint_list.append(swcPoint(0,0,0,0,0,0,0)) # an empty point numbered 0

    for point in point_list:
        temp_swcPoint = swcPoint(point[0], point[1], point[2], point[3], point[4], point[5], point[6])
        if not temp_swcPoint.p == -1:
            parent = swcPoint_list[int(temp_swcPoint.p)]
            parent.s.append(temp_swcPoint.n)
        swcPoint_list.append(temp_swcPoint)

    return (swcPoint_list)

def Writeswc(filepath, swcPoint_list, reversal = False, limit = [256, 256, 128], overlay = False, number_offset = 0):
    lines = []
    for temp_swcPoint in swcPoint_list:
        if(reversal):
            line = "%d %d %f %f %f %f %d\n" %(
                temp_swcPoint.n + number_offset, temp_swcPoint.si, temp_swcPoint.x,
                limit[1] - temp_swcPoint.y,
                temp_swcPoint.z, temp_swcPoint.r, temp_swcPoint.p + number_offset
            )
        else:
            line = "%d %d %f %f %f %f %d\n" %(
                temp_swcPoint.n + number_offset, temp_swcPoint.si, temp_swcPoint.x,
                temp_swcPoint.y,
                temp_swcPoint.z, temp_swcPoint.r, temp_swcPoint.p + number_offset
            )
        lines.append(line)
    if(overlay and os.path.exists(filepath)):
        # print("!!!!!!")
        os.remove(filepath)
    file_handle = open(filepath, mode = "a")
    file_handle.writelines(lines)
    file_handle.close()

def GetswcPointAncestor(swcPoint_list, temp_swcPoint):
    if(temp_swcPoint.p == -1):
        return temp_swcPoint.n
    else:
        return GetswcPointAncestor(swcPoint_list, swcPoint_list[temp_swcPoint.p])

def AddNewFiber(swcPoint_list, fiber_list, fiber_count, temp_swcPoint):
    fiber_count = fiber_count + 1
    temp_swcFiber = swcFiber(fiber_count)
    while (True):
        temp_swcFiber.sp.append(temp_swcPoint.n)
        swcPoint_list[temp_swcPoint.n].fn = fiber_count
        temp_swcFiber.l = temp_swcFiber.l + 1
        # temp_swcFiber.Printswc()

        if (not len(temp_swcPoint.s) == 1):  # no son or have sons
            break
        temp_swcPoint = swcPoint_list[temp_swcPoint.s[0]]

    swcPoint_list = temp_swcFiber.UpdateEnd(swcPoint_list)
    fiber_list.append(temp_swcFiber)
    if(debug_mode == 1):
        temp_swcFiber.Printswc()
    return swcPoint_list, fiber_list, fiber_count

def BuildFiberList(swcPoint_list):
    fiber_list = []
    fiber_count = 0
    fiber_list.append(swcFiber(0)) # an empty fiber numbered 0

    for temp_swcPoint in swcPoint_list:
        if(temp_swcPoint.n == 0):
            continue
        if(temp_swcPoint.p == -1): # is an Ancestor
            # temp_swcPoint.printswc()
            swcPoint_list, fiber_list, fiber_count = AddNewFiber(swcPoint_list, fiber_list, fiber_count, temp_swcPoint)
            # time.sleep(5)
        elif(len(swcPoint_list[temp_swcPoint.p].s) > 1): # have brothers
            swcPoint_list, fiber_list, fiber_count = AddNewFiber(swcPoint_list, fiber_list, fiber_count, temp_swcPoint)
        else:
            pass

    print(str(fiber_count) + " fibers have been built!")
    if(debug_mode == 1):
        isolated_count = 0
        for temp_swcPoint in swcPoint_list:
            if(temp_swcPoint.n == 0):
                continue
            if(temp_swcPoint.fn == -1):
                print(temp_swcPoint.n)
                isolated_count = isolated_count + 1
        print(str(isolated_count) + " isolated point found!")

    if(debug_mode == 5):
        test_filepath = "E://KaifengChen//neuTube_plus//dataset//result//256//segments_test//test.swc"
        fiber_list[1].Writeswc(test_filepath, swcPoint_list)
        fiber_list[2].Writeswc(test_filepath, swcPoint_list)

    return fiber_list

def CalcswcPointDist(swcPointA, swcPointB):
    return math.sqrt(
        (swcPointA.x - swcPointB.x) ** 2 +
        (swcPointA.y - swcPointB.y) ** 2 +
        (swcPointA.z - swcPointB.z) ** 2
    )

def UpdateListNeighbor(swcPoint_list, dist_tho = 10):
    for i in range(1, len(swcPoint_list)):
        for j in range(i + 1, len(swcPoint_list)):
            swcPointA = swcPoint_list[i]
            swcPointB = swcPoint_list[j]
            if(swcPointA.fn == swcPointB.fn):continue
            if(CalcswcPointDist(swcPointA, swcPointB) > dist_tho):continue

            temp_neighbor = [swcPointB.n, False]
            if(not temp_neighbor in swcPoint_list[i].neighbor):
                swcPoint_list[i].neighbor.append(temp_neighbor)
            temp_neighbor = [swcPointA.n, False]
            if(not temp_neighbor in swcPoint_list[j].neighbor):
                swcPoint_list[j].neighbor.append(temp_neighbor)

    if(debug_mode == 323):
        for swcPointA in swcPoint_list:
            if(swcPointA.neighbor):
                print(swcPointA.neighbor)

    return swcPoint_list

def CmpswcNeighbor(neigA, neigB):
    return neigA.dist < neigB.dist

def UpdateListswcNeighbor(swcPoint_list, dist_tho = 10):
    for i in range(1, len(swcPoint_list)):
        for j in range(i + 1, len(swcPoint_list)):
            swcPointA = swcPoint_list[i]
            swcPointB = swcPoint_list[j]
            if(swcPointA.fn == swcPointB.fn):continue
            temp_dist = CalcswcPointDist(swcPointA, swcPointB)
            if(temp_dist > dist_tho):continue

            temp_neig = swccmpPoint(swcPointB.n, temp_dist)
            if(not temp_neig in swcPoint_list[i].swcNeig):
                swcPoint_list[i].swcNeig.append(temp_neig)
            temp_neig = swccmpPoint(swcPointA.n, temp_dist)
            if(not temp_neig in swcPoint_list[j].swcNeig):
                swcPoint_list[j].swcNeig.append(temp_neig)
    for p in swcPoint_list:
        if(p.swcNeig):
            p.swcNeig.sort()
            # for n in p.swcNeig:
            #     n.Printswc()
            # print("--------")
            swcPoint_list[p.n] = p

    return swcPoint_list

def UpdateListswcNeighborR(swcPoint_list):
    for i in range(1, len(swcPoint_list)):
        for j in range(i + 1, len(swcPoint_list)):
            swcPointA = swcPoint_list[i]
            swcPointB = swcPoint_list[j]
            if(swcPointA.fn == swcPointB.fn):continue
            temp_dist = CalcswcPointDist(swcPointA, swcPointB)
            if(temp_dist > (swcPointA.r + swcPointB.r) * 1.2):continue

            temp_neig = swccmpPoint(swcPointB.n, temp_dist)
            if(not temp_neig in swcPoint_list[i].swcNeig):
                swcPoint_list[i].swcNeig.append(temp_neig)
            temp_neig = swccmpPoint(swcPointA.n, temp_dist)
            if(not temp_neig in swcPoint_list[j].swcNeig):
                swcPoint_list[j].swcNeig.append(temp_neig)
    for p in swcPoint_list:
        if(p.swcNeig):
            p.swcNeig.sort()
            # for n in p.swcNeig:
            #     n.Printswc()
            # print("--------")
            swcPoint_list[p.n] = p

    return swcPoint_list

def CalcVectorMod(vector3d_A): # 模
    res = math.sqrt(
        vector3d_A[0] ** 2 +
        vector3d_A[1] ** 2 +
        vector3d_A[2] ** 2
    )
    # print(res)
    return res

def CalcVectorDot(vector3d_A, vector3d_B): # 向量的点积
    res = vector3d_A[0] * vector3d_B[0] + \
           vector3d_A[1] * vector3d_B[1] + \
           vector3d_A[2] * vector3d_B[2]
    # print("dot " + str(res))
    return res

def CalcVectorAngle(vector3d_A, vector3d_B):
    # print(vector3d_A, vector3d_B)
    res = CalcVectorDot(vector3d_A, vector3d_B) / \
        (CalcVectorMod(vector3d_A) *
         CalcVectorMod(vector3d_B))


    # print(res)
    if(res > 1): res = 1
    if(res < -1): res = -1
    res = math.acos(res)
    # print(res)
    if(res > 3.1415 / 2): res = 3.1415 - res
    return res

def ClearSP(swcPoint_list):
    for swcPointA in swcPoint_list:
        for s in swcPointA.s:
            if(not swcPoint_list[s].fn == swcPointA.fn):
                swcPointA.s = []
                swcPoint_list[swcPointA.n] = swcPointA
                break
    for swcPointA in swcPoint_list:
        if(not swcPoint_list[swcPointA.p].fn == swcPointA.fn):
            swcPointA.p = -1
            swcPoint_list[swcPointA.n] = swcPointA
    return swcPoint_list

def SimpleFlipPoint(swcPointA, swcPoint_list):
    temp_s = []
    temp_p = swcPointA.p
    for s in swcPointA.s:
        if (swcPoint_list[s].fn == swcPointA.fn):
            swcPointA.p = s
        else:
            temp_s.append(s)
    if (not temp_p == -1):
        temp_s.append(temp_p)
    swcPointA.s = temp_s
    swcPoint_list[swcPointA.n] = swcPointA
    return swcPoint_list

def FlipPoint(swcPointA, swcPoint_list, swcFiber_list):
    if (swcPointA.ishead or swcPointA.istail):
        if (swcPointA.ishead):
            swcPointA.ishead = False
            swcPointA.istail = True
            if(not swcPointA.p == -1):
                if(not swcPoint_list[swcPointA.p].fn == swcPointA.fn):
                    swcPoint_list, swcFiber_list = FlipFiber(swcFiber_list[swcPoint_list[swcPointA.p].fn],
                                                             swcPoint_list, swcFiber_list)
                    # swcPoint_list = SimpleFlipPoint(swcPointA, swcPoint_list)
                else: exit(33330)
        elif (swcPointA.istail):
            swcPointA.ishead = True
            swcPointA.istail = False
            for s in swcPointA.s:
                if(not swcPoint_list[s].fn == swcPointA.fn):
                    swcPoint_list, swcFiber_list = FlipFiber(swcFiber_list[swcPoint_list[s].fn],
                                                             swcPoint_list, swcFiber_list)

    swcPoint_list = SimpleFlipPoint(swcPointA, swcPoint_list)
    return swcPoint_list

def FlipFiber(swcFiberA, swcPoint_list, swcFiber_list):
    for sp in swcFiberA.sp:
        swcPointA = swcPoint_list[sp]
        # if(len(swcPointA.s) > 1): exit(327)
        swcPoint_list = FlipPoint(swcPointA, swcPoint_list, swcFiber_list)

    # swcPoint_list = swcFiberA.UpdateEnd(swcPoint_list)
    temp = swcFiberA.ep[0]
    swcFiberA.ep[0] = swcFiberA.ep[1]
    swcFiberA.ep[1] = temp
    # print(swcPoint_list)
    swcFiber_list[swcFiberA.fn] = swcFiberA
    return swcPoint_list, swcFiber_list


def SimpleConnFiber(swcFiberA, swcFiberB, swcPoint_list, swcFiber_list, origin_swcFiber_list, dist_tho = 5):
    if(swcFiberA.state == False or swcFiberB.state == False):
        return False, swcPoint_list, swcFiber_list, origin_swcFiber_list
    if (swcFiberA.fn == swcFiberB.fn):
        return False, swcPoint_list, swcFiber_list, origin_swcFiber_list
    res = 0
    for epA in swcFiberA.ep:
        for epB in swcFiberB.ep:
            if(CalcswcPointDist(swcPoint_list[epA], swcPoint_list[epB]) < dist_tho):
                swcPointA = swcPoint_list[epA]
                swcPointB = swcPoint_list[epB]
                # print(swcFiberA.ep)
                # print(swcFiberB.ep)
                if(len(swcPointA.s) == 0 and swcPointB.p == -1): # AB
                    swcPointB.p = swcPointA.n
                    swcPointA.s.append(swcPointB.n)
                    swcFiberA.l = swcFiberA.l + swcFiberB.l
                    swcFiberA.sp.extend(swcFiberB.sp)
                    swcFiberA.UpdateEnd()
                    for mf in swcFiberB.mf:
                        if(not mf in swcFiberA.mf):
                            swcFiberA.mp.append(mf)
                            origin_swcFiber_list[mf].mf.append(swcFiberA.fn)
                        origin_swcFiber_list[mf].mf.remove(swcFiberB.fn)
                    swcFiberB.state = False
                    res = 1
                elif(swcPointA.p == -1 and len(swcPointB.s) == 0): # BA
                    swcPointA.p = swcPointB.n
                    swcPointB.s.append(swcPointA.n)
                    swcFiberB.l = swcFiberA.l + swcFiberB.l
                    swcFiberB.sp.extend(swcFiberA.sp)
                    swcFiberB.UpdateEnd()
                    for mf in swcFiberA.mf:
                        if(not mf in swcFiberB.mf):
                            swcFiberB.mp.append(mf)
                            origin_swcFiber_list[mf].mf.append(swcFiberB.fn)
                        origin_swcFiber_list[mf].mf.remove(swcFiberA.fn)
                    swcFiberA.state = False
                    res = 2
                else: # flip
                    swcPoint_list = FlipFiber(swcFiberB, swcPoint_list)
                    swcPointB = swcPoint_list[epB]
                    if (len(swcPointA.s) == 0 and swcPointB.p == -1):
                        swcPointB.p = swcPointA.n
                        swcPointA.s.append(swcPointB.n)
                        swcFiberA.l = swcFiberA.l + swcFiberB.l
                        swcFiberA.sp.extend(swcFiberB.sp)
                        swcFiberA.UpdateEnd()
                        for mf in swcFiberB.mf:
                            if (not mf in swcFiberA.mf):
                                swcFiberA.mp.append(mf)
                                origin_swcFiber_list[mf].mf.append(swcFiberA.fn)
                            origin_swcFiber_list[mf].mf.remove(swcFiberB.fn)
                        swcFiberB.state = False
                        res = 1
                    elif (swcPointA.p == -1 and len(swcPointA.s) == 0):
                        swcPointA.p = swcPointB.n
                        swcPointB.s.append(swcPointA.n)
                        swcFiberB.l = swcFiberA.l + swcFiberB.l
                        swcFiberB.sp.extend(swcFiberA.sp)
                        swcFiberB.UpdateEnd()
                        for mf in swcFiberA.mf:
                            if (not mf in swcFiberB.mf):
                                swcFiberB.mp.append(mf)
                                origin_swcFiber_list[mf].mf.append(swcFiberB.fn)
                            origin_swcFiber_list[mf].mf.remove(swcFiberA.fn)
                        swcFiberA.state = False
                        res = 2
                    else:
                        exit(32777)
                swcPoint_list[epA] = swcPointA
                swcPoint_list[epB] = swcPointB
                swcFiber_list[swcFiberA.fn] = swcFiberA
                swcFiber_list[swcFiberB.fn] = swcFiberB
                return res, swcPoint_list, swcFiber_list, origin_swcFiber_list
    return False, swcPoint_list, swcFiber_list, origin_swcFiber_list

def BendFiber(swcPointA, swcPoint_list):
    nowPoint = swcPoint_list[swcPointA.p]
    temp_point_list = []
    while(True):
        temp_point_list.append(nowPoint)
        if (nowPoint.p == -1):
            # print("ok")
            break
        nowPoint = swcPoint_list[nowPoint.p]

    for swcPointB in temp_point_list:
        swcPoint_list = FlipPoint(swcPointB, swcPoint_list)

    if(not swcPointA.p == -1):
        swcPointA.s.append(swcPointA.p)
    swcPointA.p = -1
    swcPoint_list[swcPointA.n] = swcPointA

    return swcPoint_list


def ConnFiber(swcPoint_list, swcFiber_list, swcPointA, swcPointB):
    if ((not swcPointA.istail) and (not swcPointA.ishead) and (not swcPointB.istail) and (not swcPointB.ishead)):
        return swcPoint_list, swcFiber_list
        swcPoint_list = BendFiber(swcPointA, swcPoint_list)
        swcPointB.s.append(swcPointA.n)
    else:
        if((not swcPointA.istail) and (not swcPointA.ishead)):
            tempPoint = swcPointA
            swcPointA = swcPointB
            swcPointB = tempPoint
        if(not swcPointA.ishead):
            swcFiberA = swcFiber_list[swcPointA.fn]
            swcPoint_list, swcFiber_list = FlipFiber(swcFiberA, swcPoint_list, swcFiber_list)
            swcPointA = swcPoint_list[swcFiberA.ep[0]]

    swcPointB.s.append(swcPointA.n)
    swcPointA.p = swcPointB.n
    swcPoint_list[swcPointA.n] = swcPointA
    swcPoint_list[swcPointB.n] = swcPointB
    return swcPoint_list, swcFiber_list




if __name__ == '__main__':
    # home_path = 'C://Users//12626//Desktop//seu-allen//neuTube_win64.2018.07.12//neutube_ws2//raw//'
    home_path = "E://KaifengChen//neuTube_plus//dataset//result//256//segments//"

    processed_num = 0
    for filepath, dirnames, filenames in os.walk(home_path):
        for filename in filenames:
            if(".swc" not in filename):
                continue
            file_AbsolutePath = os.path.join(filepath, filename)
            print("Processing file %s ..." %(file_AbsolutePath))

            swcPoint_list = Readswc(os.path.join(filepath, filename))
            swcFiber_list = BuildFiberList(swcPoint_list)

            processed_num = processed_num + 1
            print(str(processed_num) + "/" + str(len(filenames)) + " files had been processed!\n")




