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
    allSorifa =[]
    with open('./ClentFactures.csv','r') as f: # Internet2017.csv venteshisto.csv
       
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            ## print(l)
            if l['Sorifa'] not in allSorifa:
                allSorifa.append(l['Sorifa'])
            if l['Parent']  not in allSorifa:
                allSorifa.append(l['Parent'])
    qry = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa])+')'
    ## print(qry)
    ## allBysorifa =  sf.query_all(qry)
    print(,len(allSorifa))
if __name__== '__main__':
    process()