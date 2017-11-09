import sys
import csv 


leadbyHDF ={}

with open('./leadsAconv.csv','r') as leads:
    reader = csv.DictReader(leads, delimiter=';')
    for l in reader:
        leadbyHDF[l['HDF']]  =  l['nom']
prnit(len(leadbyHDF))
with open('./venteshisto.csv','r') as ventes:
    reader = csv.DictReader(ventes, delimiter=';') 
    for l in reader:
        if l['Code client sorifa'] in leadbyHDF.keys():
            print(l)