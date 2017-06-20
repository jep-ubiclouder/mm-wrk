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

def sendmail(insertions):

    # Import smtplib for the actual sending function
    import smtplib
    
    # Import the email modules we'll need
    
    html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
        Voici les resultats du batch de cette nuit<br>
        Lignes créées : %s
        
    </p>
  </body>
</html>
""" %(len (insertions))
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'resultat du jour'
    msg['From'] = 'ubunutu@localhost'
    msg['To'] = 'jean-eric.preis@ubiclouder.com'
    
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def findFile(parmDate):
    
    base ='./bucket-mm-daily/EXPORT_%s.CSV'%parmDate
    return base
    
def process(parmDate):
    sf = Salesforce(username='jep@assembdev.com', password='ubi$2017', security_token='aMddugz7oc45l1uhqWAE308Z', sandbox=True)
    import os.path
    import csv
    mapFields = {}
    mapfile = open('./bucket-mm-daily/mapping_lignes-de-commandes2017.sdl','r')
    for l in mapfile.readlines():
        if l[0] =='#':
            continue
        (clefSTX,clefSF) = l.split('=')
        mapFields[clefSTX]=clefSF[:-1]
    print( mapFields)
    i=0
    updates ={}
    insertions ={}
    
    with open(findFile(parmDate), 'r',encoding='utf-8') as csvfile:
        reader=  csv.DictReader(csvfile,delimiter=',')
        for row in reader:
            record={}
            statut = row['STATUT'] 
            commande=row['COMMANDE']
            if commande=='123456':continue
            Index_STOCKX__c = row['IND']
            for clef in row.keys():
                if clef =='IND': 
                    continue 
                    ## Nous faisons des upsert le champs Index_STOCKX__c NE DOIT PAS apparraitre dans le record
                if clef in mapFields.keys():
                    ## passage en AA-MM-JJ
                    if clef=='DATE_CDE' or clef == 'PARUTION':
                        ## print(clef, row[clef])                    
                        (d,m,a) = row[clef].split('-')
                        value= '%s-%s-%s'%(a,m,d)
                        row[clef]=value
                    try: 
                        record[mapFields[clef]]=row[clef]
                    except :
                        print('ooops')
            try:
                insertions[Index_STOCKX__c] = record
                pass
            except :
               continue
            i += 1
    
        for clef in insertions.keys() :
            try:
                reponse = sf.Lignes_commande__c.upsert('Index_STOCKX__c/%s'%clef,insertions[clef], raw_response=True)
            except simple_salesforce.api.SalesforceMalformedRequest:
                print(reponse.text)
            #  print(reponse)
        # print(dir(reponse))   
        sendmail(insertions)
    
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
    process(compactDate) 
