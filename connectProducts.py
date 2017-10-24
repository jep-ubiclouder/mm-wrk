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
    qry =  'select id,Code_EAN_EURODEP__c from Commande__c where Code_EAN_EURODEP__c != null'
    allLignes = sf.query_all(qry)
    
    allMissing = []
    recs = allLignes['records']
    for r in recs:
        if r['Code_EAN_EURODEP__c'] not in allMissing:
            allMissing.append(r['Code_EAN_EURODEP__c'][:-1])
    print(allMissing)
    
    qrygetProducts = 'select id,EAN__c from Product2 where EAN__C in ( \'PLACEHOLDER\',' + ','.join(["\'%s\'" % c for c in allMissing]) + ')'
    print(qrygetProducts)
    allProductId = sf.query(qrygetProducts)
    print(allProductId('records'))
    pass
if __name__ == '__main__':
    processFile()
