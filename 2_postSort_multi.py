# -*- coding: utf-8 -*-

import csv
import sys
import math
import re
import random
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import shutil
import os
import subprocess

############# パラメータ #################
seed = 1
threshold = 50
kNearestNeighbor = 5
file = 'triangles_15_200_0_3_240_240_0_0_10_170_4000x4000_bugfix.csv'
#deleteMethod = "random"
#deleteMethod = "minNov"
#deleteMethod = "minNovE"
#deleteMethod = "maxNovE"
#deleteMethod = "edgeDiff"
#deleteMethod = "edgeDiffMinNov"
#deleteMethod = "angleDiff"
deleteMethod = "minNovE_minNovE_edgeDiff"
############# パラメータ #################
t = pd.read_csv(file, header=None)
t.columns = ["P0", "P1", "P2", "A0", "A1", "A2", "L0", "L1", "L2", "Cx", "Cy", "Sx", "Sy", "E"]
maxX = t.Sx.max()
maxY = t.Sy.max()

if(deleteMethod == "edgeDiffMinNov"):
    t["edgeDiff"] = t["L2"] - t["L0"]

points = []

# ランダム削除
def randomDeletion(triangles):
   triangles.pop(random.randint(0, len(triangles) - 1))
   return triangles

# ノベルティ計算
def calcNovelty(triangles):
    novelties = []
    for triangle in triangles:
        tmpNovelties = []
        for target in triangles:
            tmpNovelties.append(math.sqrt(pow(float(triangle[12]) - float(target[12]), 2) + pow(float(triangle[13]) - float(target[13]), 2)))
        
        tmpNovelties.sort()
        novelty = 0
        for i in range(kNearestNeighbor if kNearestNeighbor < len(triangles) else len(triangles)):
            novelty = novelty + tmpNovelties.pop(0)

        novelties.append(novelty)

    return novelties

def deleteFromMiniNovelty(triangles):
    novelties = calcNovelty(triangles)

    minValue = min(novelties)
    for i in range(len(triangles)):
        if novelties[i] == minValue:
            triangles.pop(i)
            return triangles

    # 消されなかった場合
    return randomDeletion(triangles)

def deleteFromMaxNovelty(triangles):
    novelties = calcNovelty(triangles)

    maxValue = max(novelties)
    for i in range(len(triangles)):
        if novelties[i] == maxValue:
            triangles.pop(i)
            return triangles

    # 消されなかった場合
    return randomDeletion(triangles)

def countPoint(triangle):
    for point in points:
        if (point[0] == triangle[0] and point[1] == triangle[1]):
            point[2] = point[2] + 1
            return

    points.append([triangle[0], triangle[1], 1])
    return

def evaluateUsingCommonPointsTriangles(triangles):
    for triangle in triangles:
        countPoint(triangle)

    value = []
    v = 0
    for triangle in triangles:
        for point in points:
            if(point[0] == triangle[0] and point[1] == triangle[1]):
                v = v + point[2]
        value.append(v)

    return value

def deleteCommonPointTriangle(triangles):
    value = evaluateUsingCommonPointsTriangles(triangles)

    M = max(value)
    for i in range(len(triangles)):
        if M == value[i]:
            triangles.pop(i)
            return triangles

    # 消されなかった場合
    return randomDeletion(triangles)

def deleteCharacteristicPointTriangle(triangles):
    value = evaluateUsingCommonPointsTriangles(triangles)

    M = min(value)
    for i in range(len(triangles)):
        if M == value[i]:
            triangles.pop(i)
            return triangles

    # 消されなかった場合
    return randomDeletion(triangles)

# 2番目角度計算
def calcAngle2(triangles):
    angles = []
    for triangle in triangles:
        angles.append(triangle[4])

    return angles

# 内角で削除
def interiorAngleDeletion(triangles):
    angles = calcAngle2(triangles)
    m = min(angles)

    for i in range(len(triangles)):
        if m == triangles[i][4]:
            triangles.pop(i)
            return triangles

    # 消されなかった場合
    return randomDeletion(triangles)


def calcNoveltyA(triangle):
    arrX = np.ones(triangle.shape[0]) * float(triangle[0:1].Cx)
    for i in range(1, triangle.shape[0]):
        arrX = np.c_[arrX, np.ones(triangle.shape[0]) * float(triangle[i: i+1].Cx)]

    arrY = np.ones(triangle.shape[0]) * float(triangle[0:1].Cy)
    for i in range(1, triangle.shape[0]):
        arrY = np.c_[arrY, np.ones(triangle.shape[0]) * float(triangle[i: i+1].Cy)]

    diffX = arrX - arrX.T
    diffX = diffX ** 2
    diffY = arrY - arrY.T
    diffY = diffY ** 2

    diff = diffX + diffY

    s = 0
    for i in diff[0].argsort()[0:kNearestNeighbor]:
        s = s + diff[0][i]

    diffNeighbor = np.ones(1) * s

    for r in range(1, diff.shape[0]):
        s = 0
        for i in diff[r].argsort()[0:kNearestNeighbor]:
            s = s + diff[r][i]
        diffNeighbor = np.c_[diffNeighbor, np.ones(1) * s]
    
    return diffNeighbor

def calcNoveltyE(triangle):
    arrX = np.ones(triangle.shape[0]) * float(triangle[0:1].E)
    for i in range(1, triangle.shape[0]):
        arrX = np.c_[arrX, np.ones(triangle.shape[0]) * float(triangle[i: i+1].E)]

    diffX = arrX - arrX.T
    diffX = diffX ** 2

    diff = diffX

    s = 0
    for i in diff[0].argsort()[0:kNearestNeighbor]:
        s = s + diff[0][i]

    diffNeighbor = np.ones(1) * s

    for r in range(1, diff.shape[0]):
        s = 0
        for i in diff[r].argsort()[0:kNearestNeighbor]:
            s = s + diff[r][i]
        diffNeighbor = np.c_[diffNeighbor, np.ones(1) * s]
    
    return diffNeighbor

def calcNoveltyEdgeDiff(triangle):
    arrX = np.ones(triangle.shape[0]) * float(triangle[0:1].edgeDiff)
    for i in range(1, triangle.shape[0]):
        arrX = np.c_[arrX, np.ones(triangle.shape[0]) * float(triangle[i: i+1].edgeDiff)]

    diffX = arrX - arrX.T
    diffX = diffX ** 2

    diff = diffX

    s = 0
    for i in diff[0].argsort()[0:kNearestNeighbor]:
        s = s + diff[0][i]

    diffNeighbor = np.ones(1) * s

    for r in range(1, diff.shape[0]):
        s = 0
        for i in diff[r].argsort()[0:kNearestNeighbor]:
            s = s + diff[r][i]
        diffNeighbor = np.c_[diffNeighbor, np.ones(1) * s]
    
    return diffNeighbor

# 短辺と長辺の差
def deleteTriangleFromEdgeDiff(triangle):
    m = triangle.L2.max()
    minIndex = -1
    for i in range(triangle.shape[0]):
        diff = int(triangle[i : i+1].L2 - triangle[i : i+1].L0)
        if diff < m:
            m = diff
            minIndex = i

    triangle = triangle.drop(triangle.index[minIndex])
    
    return triangle

# 角度の差
def deleteTriangleFromAngle(triangle):
    m = triangle.A2.max()
    minIndex = -1
    for i in range(triangle.shape[0]):
        diff = int(triangle[i : i+1].A2 - triangle[i : i+1].A0)
        if diff < m:
            m = diff
            minIndex = i

    triangle = triangle.drop(triangle.index[minIndex])
    
    return triangle

# ノベルティの最小値で削除
def deleteTriangleMinNovelty(triangle):
    novelty = calcNoveltyA(triangle)
    triangle = triangle.drop(triangle.index[novelty.argmin()])
    return triangle

# ランダムに削除
def deleteTriangleRandom(triangle):
    triangle = triangle.drop(triangle.index[random.randint(0, len(triangle) - 1)])
    return triangle

# ノベルティの最小値で削除
def deleteTriangleMinNoveltyE(triangle):
    novelty = calcNoveltyE(triangle)
    triangle = triangle.drop(triangle.index[novelty.argmin()])
    return triangle

# ノベルティの最大値で削除
def deleteTriangleMaxNoveltyE(triangle):
    novelty = calcNoveltyE(triangle)
    triangle = triangle.drop(triangle.index[novelty.argmax()])
    return triangle

# ノベルティの最小値で削除
def deleteTriangleEdgeDiffMinNovelty(triangle):
    novelty = calcNoveltyEdgeDiff(triangle)
    triangle = triangle.drop(triangle.index[novelty.argmin()])
    return triangle

def deleteTriangle(index):
    x = index // (maxY+1)
    y = index % (maxY+1)
    tmp = t[(t["Sx"] == x) & (t["Sy"] == y)]
    i = 0
    
    random.seed(index)
    print(str(x) + ", " + str(y) + ": " + str(tmp.shape[0]))
    while (tmp.shape[0] > threshold):
        if tmp.shape[0] % 10 == 0:
            print(str(x) + ", " + str(y) + ": " + str(tmp.shape[0]))
        if (deleteMethod == "minNov"):
            tmp = deleteTriangleMinNovelty(tmp)
        elif (deleteMethod == "random"):
            tmp = deleteTriangleRandom(tmp)
        elif (deleteMethod == "minNovE"):
            tmp = deleteTriangleMinNoveltyE(tmp)
        elif (deleteMethod == "maxNovE"):
            tmp = deleteTriangleMaxNoveltyE(tmp)
        elif (deleteMethod == "edgeDiff"):
            tmp = deleteTriangleFromEdgeDiff(tmp)
        elif (deleteMethod == "edgeDiffMinNov"):
            tmp = deleteTriangleEdgeDiffMinNovelty(tmp)
        elif (deleteMethod == "angleDiff"):
            tmp = deleteTriangleFromAngle(tmp)
        elif (deleteMethod == "minNovE_minNovE_edgeDiff"):
            if (i % 3 == 0):
                tmp = deleteTriangleMinNoveltyE(tmp)
                i = i + 1
            elif (i % 3 == 1):
                tmp = deleteTriangleMinNoveltyE(tmp)
                i = i + 1
            elif (i % 3 == 2):
                tmp = deleteTriangleFromEdgeDiff(tmp)
                i = i + 1

    tmp.to_csv("tmp/" + str(x) + "_" + str(y) + "_" + re.sub('.csv', '_' + str(deleteMethod) + '_' + str(threshold) + "_" + str(kNearestNeighbor) + '.csv', file), header=False, index=False, mode="a")

if __name__ == "__main__":
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")
    os.mkdir("tmp")
    with ProcessPoolExecutor() as executor:
        for i in range(maxX + 1):
            for j in range(maxY + 1):
                executor.submit(deleteTriangle, i * (maxY+1) + j)
        
    fileName = str(re.sub('.csv', '_' + str(deleteMethod) + '_' + str(threshold) + "_" + str(kNearestNeighbor) + '.csv', file))

    returncode = subprocess.call("type tmp\*.csv > " + fileName, shell=True)