import sys
import csv 
from simple_salesforce import (Salesforce, SalesforceAPI, SFType, SalesforceError, SalesforceMoreThanOneRecord, SalesforceExpiredSession, SalesforceRefusedRequest,
    SalesforceResourceNotFound, SalesforceGeneralError, SalesforceMalformedRequest)

def process():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allProduits = []
    with open('./Fev2017.csv','r') as f: # Internet2017.csv venteshisto.csv
        allSorifa =[]
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            if l['article'] not in allProduits:
                allProduits.append(l['article'])

    print(allProduits,len(allProduits))
if __name__ == '__main__':
    process()


