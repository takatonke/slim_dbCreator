# -*- coding: utf-8 -*-

import csv
import sys
import re


ff = 'triangles_15_200_0_3_240_240_0_0_10_170_4000x4000_bugfix_minNovAcc_50_5_minNovAcc_17_5_170_35.csv'
f = open(ff, 'r')
dataReader = csv.reader(f)

wf = re.sub('.csv', '_del.csv', ff)
writeFile = open(wf, 'w')
writer = csv.writer(writeFile, lineterminator='\n')


# 点の読み込み(ソート前提)
rows = []
for row in dataReader:
    del row[13]
    del row[10]
    del row[9]

    rows.append(row)

for a in range(len(rows)):
    writer.writerow(rows[a])

f.close()
writeFile.close()

print (u'完了')