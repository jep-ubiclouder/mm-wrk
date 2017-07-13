#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 8 juin 2017

@author: jean-eric preis
'''
from simple_salesforce import Salesforce
import sys
from _datetime import timedelta
from datetime import date
from ftplib import FTP


def getfromFTP(compactDate):
    print(compactDate)
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')

    truc = eurodep.nlst('*%s.csv' % compactDate)
    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]


def findUnknownItems(connus, fournis):
    resultat = []
    for k in fournis:
        if k not in connus:
            resultat.append(k)
    return resultat 
def processFile(fname):
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
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')

    import os.path
    import csv
    print(fname)
    codes_cli = []
    eans = []
    arts = []
    connus =[]
    with open(fname, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            print('Code Client', row['CODCLI'])
            if row['CODCLI'] not in codes_cli:
                codes_cli.append("%s" % row['CODCLI'])
            if row['ART'] not in arts:
                arts.append(row['ART'])
            if row['EAN ART'] not in eans:
                eans.append(row['EAN ART'])
        # print(row)
    print(codes_cli)
    qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (' + ','.join([
        "\'%s\'" % c for c in codes_cli]) + ')'

    les_ids = sf.query(qry_code_eurodep)
    for acc in les_ids['records']:
        print(acc)
        connus.append(acc['Code_EURODEP__c'])
    clientsInconnus= findUnknownItems(connus,codes_cli)
    
    connus=[]
    qry_eans = 'select id,name,Code_ACL__c,EAN__c from product2 where EAN__c in (' + ','.join([
        "\'%s\'" % c for c in eans]) + ')'
    les_eans = sf.query(qry_eans)
    for prod in les_eans['records']:
        print("EAN",prod)
        connus.append(prod['EAN__c'])
    EANInconnus= findUnknownItems(connus, eans)
    
        
    qry_arts = 'select id,name,Code_ACL__c,EAN__c from product2 where Code_ACL__c in (' + ','.join([
        "\'%s\'" % c for c in arts]) + ')'
    les_eans = sf.query(qry_arts)
    for prod in les_eans['records']:
        print("ART",prod)
        
    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")

    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
    compactDate = '%s%02i%02i' % (now.year, now.month, now.day)
    fn = getfromFTP(compactDate)
    processFile(fn)
