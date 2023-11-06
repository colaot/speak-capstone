#!/usr/bin/env python3
import csv


input = open("test_strings.txt","r")

with open('testingCM.csv', newline = '') as csvfile:
    reader = csv.DictReader(csvfile)
    keys = []
    vals = []
    for row in reader:
        keys.append(row["Chord"])
        vals.append(row["Word"])

    chordDict = {keys[i]:vals[i] for i in range(len(keys))}
    
input = open("test_strings.txt", "r")

for line in input:
    if line[:-1] in chordDict:
        print(chordDict.get(line[:-1]))
    else:
        print(line[:-1])
input.close()
