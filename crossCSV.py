import sys
import csv 
from simple_salesforce import (Salesforce, SalesforceAPI, SFType, SalesforceError, SalesforceMoreThanOneRecord, SalesforceExpiredSession, SalesforceRefusedRequest,
    SalesforceResourceNotFound, SalesforceGeneralError, SalesforceMalformedRequest)

def process():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    allComptes =[]
    with open('./Fev2017.csv','r') as f: # Internet2017.csv venteshisto.csv
        allSorifa =[]
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['Code Ean'] not in allProduits:
                allProduits.append(l['Code Ean'])
            if l['code client Eurodep'] not in allComptes:
                allComptes.append(l['code client Eurodep'])

    print(allProduits,len(allProduits))
    qryAllProductBySORIFA = 'select id,EAN__c,Name from Product2 where EAN__c in ('+','.join(["\'%s\'" % c for c in allProduits])+')'
    
    print(qryAllProductBySORIFA)
    recsP = sf.query_all(qryAllProductBySORIFA)['records']
    print(len(recsP))
    
    print(allComptes,len(allComptes))
    qryAllComptes = 'select id,Code_EURODEP__c,Name from Account where Code_EURODEP__c in ('+','.join(["\'%s\'" % c for c in allComptes])+')'
    recsA = sf.query_all(qryAllComptes)['records']
    print(len(allComptes), len(recsA))
    
if __name__ == '__main__':
    process()


