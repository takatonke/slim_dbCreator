# -*- coding: utf-8 -*-

import csv
import sys
import math
import re
import random
from operator import itemgetter, attrgetter

blockLength = 35

ff = 'triangles_15_200_0_3_240_240_0_0_10_170_4000x4000_bugfix_minNovAcc_50_5_minNovAcc_17_5.csv'
f = open(ff, 'r')
dataReader = csv.reader(f)

wf = re.sub('.csv', '_170_' + str(blockLength) + '.csv', ff)
writeFile = open(wf, 'w')
writer = csv.writer(writeFile, lineterminator='\n')


# 点の読み込み(ソート前提)
rows = []
for row in dataReader:
    row[11] = int(int(row[9])/blockLength)
    row[12] = int(int(row[10])/blockLength)

    rows.append(row)

rows = sorted(rows, key=itemgetter(11, 12))

for a in range(len(rows)):
    writer.writerow(rows[a])

f.close()
writeFile.close()

print (u'完了')