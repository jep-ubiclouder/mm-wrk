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



def getfromFTP(compactDate,now):
    print(compactDate)
    eurodep= FTP(host='ftp.eurodep.fr',user='HOMMEDEFER',passwd='lhdf515')    
    
    truc = eurodep.nlst('*%s.csv'%compactDate)
    for t in truc:
        eurodep.retrbinary('RETR %s'%t, open('%s'%t,'wb').write)
    return truc[0]
   
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
    fn = getfromFTP(compactDate,now)
    print(fn) 