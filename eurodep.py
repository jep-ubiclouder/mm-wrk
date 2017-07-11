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
    eurodep= FTP(host='ftp.eurodep.fr',user='HOMMEDEFER',passwd='lhdf515')    
    
    truc = eurodep.nlst('*%s.csv'%compactDate)
    for t in truc:
        eurodep.retrbinary('RETR %s'%t, open('%s'%t,'wb').write)
    return truc[0]


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
    sf = Salesforce(username='jep@assembdev.com', password='ubi$2017', security_token='aMddugz7oc45l1uhqWAE308Z', sandbox=True)
    import os.path
    import csv
    print(fname)
    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d','--date', action="store", dest="parmDate")
    
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate :
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() -timedelta(days=1)
    compactDate='%s%02i%02i'%(now.year,now.month,now.day)
    fn = getfromFTP(compactDate)
    print(fn) 