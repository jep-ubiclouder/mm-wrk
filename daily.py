#!/usr/bin/python3.4
#-*- coding: utf-8 -*-

'''
Created on 8 juin 2017

@author: jean-eric preis
'''
from simple_salesforce import Salesforce
import sys
#from msilib.schema import _Validation_records
sf = Salesforce(username='jep@assembdev.com', password='ubi$2017', security_token='aMddugz7oc45l1uhqWAE308Z', sandbox=True)

toto = sf.query('select id from Lignes_commande__c')
""" for r in toto['records']:
    id=r['Id']
    print( 'deleting ',id)
    sf.Lignes_commande__c.delete(id)
while 'nextRecordUrl' in toto.keys():
    toto = sf.query_more(toto['nextRecordUrl'])
    for r in toto['records']:
        id=r['Id']
        print( 'deleting ',id)
        sf.Lignes_commande__c.delete(id) """
import os.path
import csv
mapFields = {}
mapfile = open('./bucket-mm-daily/mapping_lignes-de-commandes2017.sdl','r')
for l in mapfile.readlines():
    if l[0] =='#':
        continue
    (clefSTX,clefSF) = l.split('=')
    mapFields[clefSTX]=clefSF[:-1]
print( mapFields)
i=0
updates =[]
insertions =[]
effaces =[]
with open('./bucket-mm-daily/EXPORT_20170619.CSV', 'r',encoding='utf-8') as csvfile:
    reader=  csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        print(row)
        sys.exit(0)
        record={}
        statut = row['STATUT'] 
        for clef in row.keys():
            if clef in mapFields.keys():
                # print(clef,row[clef])
                if clef=='DATE_CDE' or clef == 'PARUTION':
                    (d,m,a) = row[clef].split('-')
                    value= '%s-%s-%s'%(a,m,d)
                    row[clef]=value
                    
                try: 
                    record[mapFields[clef]]=row[clef]
                except :
                    print('ooops')
        try:
            #print( record)
            if statut =='M': updates.append(record)
            elif statut=='C': insertions.append(record)
            elif statut =='D':effaces.append(record)
            # reponse = sf.Lignes_commande__c.create(record)
            pass
        except :
           continue
        i += 1
        if i > 30:
            break
    print(insertions)
    print(updates)    
if __name__ == '__main__':
    pass
