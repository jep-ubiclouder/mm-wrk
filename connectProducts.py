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
    #qry =  'select id,Code_EAN_EURODEP__c from Commande__c where Code_EAN_EURODEP__c != null'
    qry = 'select Code_EAN_EURODEP__c,CALENDAR_YEAR(date_de_commande__c) , sum(Quantite__c) from Commande__c  where Code_EAN_EURODEP__c != null GROUP BY CALENDAR_YEAR(date_de_commande__c),Code_EAN_EURODEP__c'
    allLignes = sf.query_all(qry)
    print(allLignes['records'])
    '''
    allMissing = []
    recs = allLignes['records']
    for r in recs:
        if r['Code_EAN_EURODEP__c'] not in allMissing:
            allMissing.append(r['Code_EAN_EURODEP__c'])
    print(allMissing)
    
    qrygetProducts = 'select id,EAN__c from Product2 where EAN__C in ( \'PLACEHOLDER\',' + ','.join(["\'%s\'" % c for c in allMissing]) + ')'
    print(qrygetProducts)
    allProductId = sf.query(qrygetProducts)
    Produits = allProductId['records']
    byEAN = {}
    
    for p in Produits:
        if p['EAN__c'] not in byEAN.keys():
            byEAN[p['EAN__c']] = p['Id'] 
    updateRex = []
    for r in recs :
        if r['Code_EAN_EURODEP__c'] in byEAN.keys():
           updateRex.append({'Id':r['Id'],'Produit__c':byEAN[r['Code_EAN_EURODEP__c']],'Code_EAN_EURODEP__c':''})
    sf.bulk.Commande__c.update(updateRex)
    '''
if __name__ == '__main__':
    processFile()
