from simple_salesforce import (
    Salesforce,
    SalesforceAPI,
    SFType,
    SalesforceError,
    SalesforceMoreThanOneRecord,
    SalesforceExpiredSession,
    SalesforceRefusedRequest,
    SalesforceResourceNotFound,
    SalesforceGeneralError,
    SalesforceMalformedRequest
)
 
import sys
from _datetime import timedelta
import datetime
import csv

def process():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    mapSorifaIds={}
    with open('./ClentFactures.csv','r') as f: # Internet2017.csv venteshisto.csv
        allSorifa =[]
        reader = csv.DictReader(f, delimiter=';')
        cpt =0
        for l in reader:
            ## print(l)
            if l['Sorifa'] not in mapSorifaIds.keys():
                allSorifa.append(l['Sorifa'])
            if l['Parent']  not in mapSorifaIds.keys():
                allSorifa.append(l['Parent'])
            cpt +=1
            if cpt> 500:
                qry = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa])+')'
                
                allBysorifa =  sf.query_all(qry)['records']
                for r in allBysorifa:
                    if r['Code_Client_SOFIRA__c'] not in mapSorifaIds.keys():
                        mapSorifaIds[r['Code_Client_SOFIRA__c']] = r['Id']
                cpt= 0
                allSorifa =[]
        
        if len(allSorifa)>0:         
            qry = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa])+')'
            print('lastquery')
            allBysorifa =  sf.query_all(qry)['records']
            for r in allBysorifa:
                if r['Code_Client_SOFIRA__c'] not in mapSorifaIds.keys():
                    mapSorifaIds[r['Code_Client_SOFIRA__c']] = r['Id']
    ## allBysorifa =  sf.query_all(qry)
    print(len(mapSorifaIds.keys()))
    with open('./ClentFactures.csv','r') as f: # Internet2017.csv venteshisto.csv
        allSorifa =[]
        allupdate =[]
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['Parent']  in mapSorifaIds.keys() and l['Sorifa']  in mapSorifaIds.keys() :
                allupdate.append({'Id': mapSorifaIds[l['Sorifa']],'ParentId':mapSorifaIds[l['Parent']]})
    res = sf.bulk.Account.update(allupdate)  
             
if __name__== '__main__':
    process()