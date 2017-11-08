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
from datetime import date

def processFile():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allSorifa =[]
    byFacture ={}
    allProducts =[]
    with('./complementfev2017.csv','r') as c:
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            # print(l['date mouvement'])
            dateclef='%s%s%s' %(l['date mouvement'][-4:],l['date mouvement'][3:5],l['date mouvement'][:2])
            ## print(dateclef)
            ## print(l['numero document']+dateclef)
            
            if (l['numero document']) not in byFacture.keys():
                byFacture[l['numero document']] = l['Code client sorifa']
            
            if l['Code client sorifa'] not in allSorifa:
                allSorifa.append(l['Code client sorifa'])
            if l['code article'] not in allProducts:
                allProducts.append(l['code article'])
               
    print('All sorifa ',len(allSorifa))
    
    qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa])+')'
    
    qryFindProduits =' select id, ProductCode from Product2 where ProductCode in ('+  ','.join(["\'%s\'" % c for c in allProducts])+')'
    
    
       
if __name__ == '__main__':
    processFile()
