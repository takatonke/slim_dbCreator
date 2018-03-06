# -*- coding: utf-8 -*-

import csv
import sys
import math
from operator import itemgetter, attrgetter
import time

def Cross(x1, y1, x2, y2):
   return x1 * y2 - y1 * x2

def IsContain(x1, y1, x2, y2, x3, y3, target_x, target_y):
   c = 0
   if (Cross((target_x - x1), (target_y - y1), (x2 - x1), (y2 - y1)) < 0):
      c += -1
   else:
      c += 1

   if (Cross((target_x - x2), (target_y - y2), (x3 - x2), (y3 - y2)) < 0):
      c += -1
   else:
      c += 1

   if (Cross((target_x - x3), (target_y - y3), (x1 - x3), (y1 - y3)) < 0):
      c += -1
   else:
      c += 1

   return 1 if (c == 3 or c == -3) else 0

argvs = sys.argv #コマンドライン引数取得

#f = open(argvs[1], 'rb')
f = open("suichoku.csv", "r")
#f = open("map_cst2_nacparam_h18000_171121.csv", 'r')

dataReader = csv.reader(f)

############# パラメータ #################
DR = 65536
DR7 = 8388608

#辺の長さの許容範囲
s = 15
b = 200

containMin = 0 #内包点の最小許容数
containMax = 3 #内包点の最大許容数

# 区画の大きさ
divX = 170
divY = 170

# 区画の大きさ
divHaruX = 240
divHaruY = 240

# 二等辺三角形の許容範囲
sameLength = 0
sameAngle = 0

# 三角形の各内角の許容範囲
thetaMin = 10
thetaMax = 170

############# パラメータ #################

points = []

# 点の読み込み
for row in dataReader:
   points.append([int(row[0]), int(row[1]), int(row[0]) / divHaruX, int(row[1]) / divHaruY, int(row[2])])

#変更前
#points = sorted(points, key=itemgetter(2, 3, 0, 1, 4))
#変更後
points = sorted(points, key=itemgetter(0, 1))

#点の一覧
pointsFile = open('craterPoints.csv', 'w')
pointsWriter = csv.writer(pointsFile, lineterminator='\n')

for i in range(len(points)):
   list = []
   list.append(str(points[i][0]))
   list.append(str(points[i][1]))
   list.append(str(points[i][2]))
   list.append(str(points[i][3]))
   pointsWriter.writerow(list)

pointsFile.close()

filename = 'triangles_' + str(s) + '_' + str(b) + '_' + str(containMin) + '_' + str(containMax) + '_' + str(divHaruX) + '_' + str(divHaruY) + '_' + str(sameLength) + '_' + str(sameAngle) + '_' + str(thetaMin) + '_' + str(thetaMax) + '_' + '4000' + 'x' + '4000_bugfix' + '.csv'
trianglesFile = open(filename, 'w')
trianglesWriter = csv.writer(trianglesFile, lineterminator='\n')

# パラメータ
#list = []
#list.append(str(DR))
#list.append(str(DR7))
#list.append(str(s))
#list.append(str(b))
#list.append(str(containMax))
#list.append(str(divX))
#list.append(str(divY))
#trianglesWriter.writerow(list)

size = len(points)
triangleList = []
timeA = time.time()
for i in range(size - 2):
   #print (str(i) + " / " + str(size - 3))
   for j in range(i + 1, size - 1):
      line_ij = math.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
      if ((line_ij < s) or (line_ij > b)):
            continue
      for k in range(j + 1, size):
         # 長さ
         line_jk = math.sqrt((points[k][0] - points[j][0]) ** 2 + (points[k][1] - points[j][1]) ** 2)
         line_ki = math.sqrt((points[k][0] - points[i][0]) ** 2 + (points[k][1] - points[i][1]) ** 2)

         #辺の長さによる制限
         if ((min(line_jk, line_ki) < s) or (max(line_jk, line_ki) > b)):
            continue

         # 二等辺三角形チェック
         #if((abs(line_ij - line_jk) < sameLength) or (abs(line_jk - line_ki) < sameLength) or (abs(line_ki - line_ij) < sameLength)):
         #   continue
         if((abs(line_ij - line_jk) < 0.1 * line_ki) or (abs(line_ij - line_ki) < 0.1 * line_jk) or (abs(line_jk - line_ki) < 0.1 * line_ij)):
               continue

         # 余弦定理で角度cos
         cos = [0, 0, 0]
         cos[0] = (line_ij ** 2 + line_ki ** 2 - line_jk ** 2) / (2 * line_ij * line_ki)
         cos[1] = (line_ij ** 2 + line_jk ** 2 - line_ki ** 2) / (2 * line_ij * line_jk)
         cos[2] = (line_jk ** 2 + line_ki ** 2 - line_ij ** 2) / (2 * line_jk * line_ki)

         #is_straight
         #10°
         #if(cos[0] > 0.984808 or cos[0] < -0.984808 or cos[1] > 0.984808 or cos[1] < -0.984808 or cos[2] > 0.984808 or cos[2] < -0.984808) :
         if(cos[0] > math.cos(math.pi * thetaMin / 180) or cos[0] < math.cos(math.pi * thetaMax  / 180) or cos[1] > math.cos(math.pi * thetaMin / 180) or cos[1] < math.cos(math.pi * thetaMax  / 180) or cos[2] > math.cos(math.pi * thetaMin / 180) or cos[2] < math.cos(math.pi * thetaMax  / 180)) :
            continue
         #checkIsoscelesTtriangle
         if((abs(cos[0]- cos[1]) < sameAngle) or (abs(cos[1] - cos[2]) < sameAngle) or (abs(cos[2] - cos[0]) < sameAngle)):
           continue

         #内包点
         
         flag = 0
         containList = []
         for a in range(size):
            ax = points[a][0]
            ay = points[a][1]
            if(a == i or a == j or a == k):
               continue
            if((max(points[i][0], points[j][0], points[k][0]) < ax) or (min(points[i][0], points[j][0], points[k][0]) > ax) or (max(points[i][1], points[j][1], points[k][1]) < ay) or (min(points[i][1], points[j][1], points[k][1]) > ay)):
               continue
            if(IsContain(points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1], ax, ay) == 1):
               flag = flag + 1
               containList.append([int(ax), int(ay)])
               if(flag > containMax):
                  break

         if((flag > containMax) or (flag < containMin) ):
            continue
        

         #if flag == 9:
         #  containList[9][0] = 0
         #  containList[9][1] = 0
         #  containList[10][0] = 0
         #  containList[10][1] = 0
         
         #if flag == 10:
         #   containList[10][0] = 0
         #   containList[10][1] = 0
         


         # cosの昇順で並び替え
         i_max = 0
         i_c = 0
         i_min = 0
         c_max = max(cos[0], cos[1], cos[2])
         c_min = min(cos[0], cos[1], cos[2])
         indexList = [i, j, k]
         for index in range(3):
            if(cos[index] == c_max):
               i_max = index
            if(cos[index] == c_min):
               i_min = index
         if((i_max == 0 and i_min == 1) or (i_max == 1 and i_min == 0)):
            i_c = 2
         elif((i_max == 0 and i_min == 2) or (i_max == 2 and i_min == 0)):
            i_c = 1
         elif((i_max == 1 and i_min == 2) or (i_max == 2 and i_min == 1)):
            i_c = 0

         list = []
         # 三角形を構成する点のindex
         list.append(indexList[i_min])
         list.append(indexList[i_c])
         list.append(indexList[i_max])
         '''
         list.append(int(points[indexList[i_min]][0] * DR))
         list.append(int(points[indexList[i_min]][1] * DR))
         list.append(int(points[indexList[i_c]][0] * DR))
         list.append(int(points[indexList[i_c]][1] * DR))
         list.append(int(points[indexList[i_max]][0] * DR))
         list.append(int(points[indexList[i_max]][1] * DR))
         '''

         list.append(int(cos[i_min] * DR))
         list.append(int(cos[i_c] * DR))
         list.append(int(cos[i_max] * DR))

         line = [line_ij, line_jk, line_ki]
         c_max = max(line_ij, line_jk, line_ki)
         c_min = min(line_ij, line_jk, line_ki)
         for index in range(3):
            if(line[index] == c_max):
               i_max = index
            if(line[index] == c_min):
               i_min = index
         if((i_max == 0 and i_min == 1) or (i_max == 1 and i_min == 0)):
            i_c = 2
         elif((i_max == 0 and i_min == 2) or (i_max == 2 and i_min == 0)):
            #ii_c = 1
            i_c = 1
         elif((i_max == 1 and i_min == 2) or (i_max == 2 and i_min == 1)):
            i_c = 0
         list.append(int(line[i_min]))
         list.append(int(line[i_c]))
         list.append(int(line[i_max]))

         # 重心
         list.append(int((points[i][0] + points[j][0] + points[k][0]) / 3))
         list.append(int((points[i][1] + points[j][1] + points[k][1]) / 3))

         # 区画(重心)
         list.append(int((points[i][0] + points[j][0] + points[k][0]) / 3 / divX))
         list.append(int((points[i][1] + points[j][1] + points[k][1]) / 3 / divY))
         listSize = len(list)

         list.append(int(points[i][4] + points[j][4] + points[k][4]))
         # 内包点
         #for l in range(len(containList)):
            #list.append(int(containList[l][0]))
            #list.append(int(containList[l][1]))

         triangleList.append(list)

# 区画でソートした後、区画内でソート
triangleList = sorted(triangleList, key=itemgetter(listSize - 2, listSize - 1, listSize - 4, listSize - 3))
timeB = time.time()
print(timeB - timeA)
for a in range(len(triangleList)):
   trianglesWriter.writerow(triangleList[a])

trianglesFile.close()

print (u'完了')
