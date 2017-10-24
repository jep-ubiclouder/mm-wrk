#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 24/10/2017

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

sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')

qryallProducts = "select id,Famille_de_Produit__c,Famille__c from Product2"
qryallFamily = "select id,Code_Famille__c from Famille_de_Produit__c "
lesProduits =les_ids = sf.query(qryallProducts)
lesFamilles =sf.query(qryallFamily)

hFamille = lesFamilles['records']
byCodeFamille = {}
for rec in hFamille:
    byCodeFamille[rec['Famille_de_Produit__c']] =rec['Id']
    
print(lesProduits)