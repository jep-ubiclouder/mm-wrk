#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 07 Novembre 2017

@author: jean-eric preis
'''
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
import csv
def process():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry  ='SELECT Bon_de_livraison__c,Code_Client_EURODEP__c,Code_EAN_EURODEP__c,Compte__c,C_A_Brut__c,C_A_Net__c,Date_de_commande__c,Facture__c,Ligne__c,Prix_Brut__c,Prix_Net__c,Produit__c,Quantite__c,Reference_Client__c FROM Commande__c where compte__c = null and Code_Client_EURODEP__c = null  order by Date_de_commande__c desc'
    ## result = sf.query_all(qry)['records']
    
    with open('./histoventes.csv','r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for l in reader:
            pass
        print( l)
if __name__ == '__main__':
    process()