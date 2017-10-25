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
from ftplib import FTP, all_errors

import codecs
import os.path
import csv

import pprint

def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        eurodep.cwd('./OUT/IMG/')
        truc = eurodep.nlst('./OIMG515%s*.CSV' % compactDate) #ftp://HOMMEDEFER@ftp.eurodep.fr/OUT/IMG/OIMG51517102400001.CSV
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]

if __name__ == '__main__':
    from datetime import datetime
    now = datetime.now() - timedelta(days=1)
    compactDate = '%02i%02i%02i' % (now.year-2000, now.month, now.day)
    print(compactDate)
    fn = getfromFTP(compactDate)
    print(fn)