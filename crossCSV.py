import sys
import csv 
from simple_salesforce import (Salesforce, SalesforceAPI, SFType, SalesforceError, SalesforceMoreThanOneRecord, SalesforceExpiredSession, SalesforceRefusedRequest,
    SalesforceResourceNotFound, SalesforceGeneralError, SalesforceMalformedRequest)

def process():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    allComptes =[]
    allSorifa =[]
    with open('./Fev2017.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['Code Ean'] not in allProduits:
                allProduits.append(l['Code Ean'])
            
            if len(l['code client Eurodep']) >3:
                if l['code client Eurodep'] not in allComptes:
                    allComptes.append(l['code client Eurodep'])
                if l['code client Eurodep'][:-3]+'515' not in allComptes:
                    allComptes.append(l['code client Eurodep'][:-3]+'515')
                if l['code client Eurodep'][:-3]+'000' not in allComptes:
                    allComptes.append(l['code client Eurodep'][:-3]+'000')

    print(allProduits,len(allProduits))
    qryAllProductBySORIFA = 'select id,EAN__c,Name from Product2 where EAN__c in ('+','.join(["\'%s\'" % c for c in allProduits])+')'
    
    print(qryAllProductBySORIFA)
    recsP = sf.query_all(qryAllProductBySORIFA)['records']
    print(len(recsP))
    ProduitsByEurodep = {}
    
    for r in recsP:
        ## print(r)
        ProduitsByEurodep[r['EAN__c']] = r['Id']
    print(allComptes,len(allComptes))
    qryAllComptes = 'select id,Code_EURODEP__c,Name from Account where Code_EURODEP__c in ('+','.join(["\'%s\'" % c for c in allComptes])+')'
    recsA = sf.query_all(qryAllComptes)['records']
    print(len(allComptes),  len(recsA))
    ComptesByEurodep ={}
    for r in recsA:
        ComptesByEurodep[r['Code_EURODEP__c']] =  r['Id']
    
    inserts =[]
    with open('./Fev2017.csv','r') as f: # Internet2017.csv venteshisto.csv        
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            try:
                Record = {}
                Record['Quantite__c'] = l['QTE'].split(',')[0] 
                Record['Facture__c'] = l['nofac']
                ## Record['Ligne__c'] =l['ligne document']
                Record['Prix_Net__c'] =  float(''.join('.'.join(l['prinet'].split(',')).split(' '))) ## l['prix vente'] 
                Record['Prix_Brut__c'] = float(''.join('.'.join(l['pbrut'].split(',')).split(' ')))
                
                # total valeur
                # '-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
                dwrk = l['datfac']
                Record['Date_de_commande__c'] = '-'.join((dwrk[-4:],dwrk[3:5],dwrk[:2]))
                clefEurodep =False
                if l['code client Eurodep'][:-3]+'000' in ComptesByEurodep.keys():
                    clefEurodep = l['code client Eurodep'][:-3]+'000'
                if l['code client Eurodep'][:-3]+'515' in ComptesByEurodep.keys():
                    clefEurodep = l['code client Eurodep'][:-3]+'515'
                if clefEurodep != False:
                    Record['Compte__c'] = ComptesByEurodep[clefEurodep]
                    
                else:
                    print('PAS DE COMPTE',l)
                    continue
                if l['Code Ean'] in  ProduitsByEurodep.keys():
                    Record['Produit__c'] =  ProduitsByEurodep[l['Code Ean']]  
                else:
                    print('PAS DE PRODUITS',l)
                    continue
            except Exception:
                print(l) 
            inserts.append(Record)
    
    print(len(inserts))
    res =  sf.bulk.Commande__c.insert(inserts)
if __name__ == '__main__':
    process()


