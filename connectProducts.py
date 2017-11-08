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
from pickle import FALSE

def processFile():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allSorifa =[]
    byFacture ={}
    allProducts =[]
    with(open('./complementfev2017.csv','r')) as f:
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
    
    allAccountIds = sf.query_all(qryFindFromSorifa)['records']
    allProductIds = sf.query_all(qryFindProduits)['records'] 
    
    
    dictAccounts = {}
    dictProds ={}
    for r in allAccountIds:
        if r['Code_Client_SOFIRA__c'] not in dictAccounts.keys():
            dictAccounts[r['Code_Client_SOFIRA__c']] = r['Id']
    for r in allProductIds:
        if r['ProductCode'] not in dictProds.keys():
            dictProds[r['ProductCode']] = r['Id']   
    
    Insertions = []
    cpt = 0        
    with(open('./complementfev2017.csv','r')) as f:
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            cpt += 1
            okAcc = False
            okPro = False
            Record = {}
            Record['Quantite__c'] = l['quantité'] 
            Record['Facture__c'] = l['numero document']
            Record['Ligne__c'] =l['ligne document']
            Record['Prix_Net__c'] = l['prix vente']
            Record['Prix_Brut__c'] = l['prix vente']
            # total valeur
            # '-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            dwrk = l['date mouvement']
            Record['Date_de_commande__c'] = '-'.join((r['dwrk'][:4],r['dwrk'][4:6],r['dwrk'][6:]))
            
            if l['code article'] in dictProds.keys():
                Record['Produit__c'] = dictProds[l['code article']]
                okPro = True
            if l['Code client sorifa'] in dictAccounts.keys():
                Record['Compte__c'] = dictAccounts[l['Code client sorifa']]
                okAcc = True
            
            if okPro and okAcc:
                Insertions.append(Record)
            else:
                print('anomalie',l['code article'],l['Code client sorifa'])
    print(Insertions)
    print('Taille insertion',len(Insertions),'lignes ds fichier',cpt)
if __name__ == '__main__':
    processFile()
