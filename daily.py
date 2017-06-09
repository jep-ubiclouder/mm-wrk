'''
Created on 8 juin 2017

@author: jean-eric preis
'''
from simple_salesforce import Salesforce
sf = Salesforce(username='jep@ubitask2.com', password='Ubi$2017', security_token='bnWf5zUKZg8hPjPP5Qein2HW')

compte = sf.query("Select  id,name from Account  where AccountNumber = 'CD656092'")
print(compte['records'])

import os.path
import csv
mapFields = {}
mapfile = open('./bucket-mm-daily/map-lignes.sdl','r')
for l in mapfile.readlines():
    if l[0] =='#':
        continue
    (clefSTX,clefSF) = l.split('=')
    mapFields[clefSTX]=clefSF[:-2]

print mapFields




with open('./bucket-mm-daily/lo-2017-test.csv', 'r') as csvfile:
        reader=  reader = csv.DictReader(csvfile,delimiter=';')
        for row in reader:
            print row

if __name__ == '__main__':
    pass
