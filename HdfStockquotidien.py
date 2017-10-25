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
    if not fn:
        sys.exit()
        
    csvFile =  open(fn,'r')
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qryProd= 'select id,ProductCode from Product2'
    res = sf.query_all(qryProd)
    byCode = {}
    tobeDel = []
    for r in res['records']:
        if r['ProductCode'] not in byCode.keys():
            byCode[r['ProductCode']] = r['Id']
            tobeDel.append(r['Id'])
            
    sf.bulk.Stock_eurodep__c.delete(tobeDel)
    for l in csvFile.readlines():
        
        ligne = l[:-1]
        rec = ligne.split(';')
        acl =  rec[2]
        des = rec[4]
        lot= rec[5]
        if len(rec[7])==8:
            ddp = '%04s-%02s-%02s'%(rec[7][-4:],rec[7][2:4],rec[7][:2])
        else:
            ddp = '2999-12-31'
        qte = rec[10]
        qteAll = rec[11]
        keyforupsert=acl+lot
        if acl in byCode.keys():
            record={'Lot__c':lot,'Produit__c':byCode[acl],'Qte_allouee__c':qteAll,'Unites_en_stock__c':qte,'name':keyforupsert,'Peremption__c':ddp}
            print(record)
            ## print(keyforupsert,des,qte,acl,lot,byCode[acl])
            reponse = sf.Stock_eurodep__c.upsert('KeyForUpsert__c/%s' % keyforupsert,record, raw_response=True)
        else:
            print(keyforupsert,des,qte,acl,lot,'ERROR')