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

eurodep= FTP(host='ftp.eurodep.fr',user='HOMMEDEFER',passwd='lhdf515')

truc =  eurodep.retrlines('LIST')

print(truc)