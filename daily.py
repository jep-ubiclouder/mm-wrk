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

def tr(s):
    return '<tr>%s</tr>'%s

def td(arr):
    ligne =''
    
    for s in arr:
        ligne +=  '<td>%s</td>'%s
    print(ligne)
    
    return ligne
def maketable(summary):
    table = ''
    liste =[]
    for clef in summary.keys():
        liste =[]
        liste.append(clef)
        liste.append(summary[clef]['Nom'])
        liste.append(summary[clef]['Num_commande'])
        liste.append(summary[clef]['montant'])
        liste.append(summary[clef]['lignes'])
        table +=  tr(td(liste))    
    return table
def sendmail(now,summary):

    # Import smtplib for the actual sending function
    import smtplib
    print(summary)
    # Import the email modules we'll need
    
    html = """\
<html>
  <head></head>
  <body>
    <p>Bonjour Marie-Noëlle !<br>
        Voici les resultats du batch pour la date:%s<br>
        
        <table>
        <tr><th>CLIENT STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Lignes</th></tr>
        %s
        </table>
    </p>
  </body>
</html>
""" %( '%02i-%02i-%s'%(now.day,now.month,now.year), maketable(summary))
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'resultat du jour'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com, marie-noelle.marx@maisonmoderne.com'
    
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    #s.quit()

def findFile(parmDate):
    
    base ='./bucket-mm-daily/EXPORT_%s.CSV'%parmDate
    return base
    
def process(parmDate,now):
    
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
    deletions ={}
    lstCLients =[]
    
    
    with open(findFile(parmDate), 'r',encoding='utf-8') as csvfile:
        reader=  csv.DictReader(csvfile,delimiter=',')
        for row in reader:
            record={}
            statut = row['STATUT'] 
            commande=row['COMMANDE']
            
            # clients uniques
            clientStx = row['CLIENT']
            action =  row['STATUT']
            #if clientStx not in lstCLients:
            #    lstClients.append(clientStx)
            
            if commande=='123456':continue
            Index_STOCKX__c = row['IND']
            for clef in row.keys():
                #if clef =='IND': 
                    #continue 
                    ## Nous faisons des upsert sur le champ Index_STOCKX__c NE DOIT PAS apparraitre dans le record
                if clef in mapFields.keys():
                    if clef=='DESIGNATION': 
                        row[clef] =row[clef][:80]
                        
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
                if action in ('C','M'):
                    insertions[Index_STOCKX__c] = record
                    pass
                else:
                    deletions[Index_STOCKX__c] = record
            except :
               continue
            
        
        
        i=1    
    #qry = 'select id,Cle_Client_STOCKX__c from account where Cle_Client_STOCKX__c in '    + ','.join("'{}'".format(u) for u in lstCLients)
    #idCSTX = sf.query(qry)
    summary={}
    
        
    for clef in insertions.keys() :
        try:
            ccstx = insertions[clef]['Cle_Client_STX__c']
            # print(insertions[clef])
            if ccstx not in summary.keys():
                summary[ccstx] = {'Num_commande':'','lignes':0, 'montant':0.00,'Nom':''}
            summary[ccstx]['Num_commande'] =insertions[clef]['COMMANDE_STX__c']
            summary[ccstx]['lignes'] +=1
            summary[ccstx]['montant'] += float(insertions[clef]['Brut_Total__c'])
            summary[ccstx]['Nom'] = insertions[clef]['NOM__c']
        except Exception  as err:
            print('exception',err)
    try:
        #for t in idCSTX['records']:
        #    if t['Cle_Client_STOCKX__c']== insertions[clef]['Cle_Client_STOCKX__c']:
        #        insertions[clef]['Compte__c']=t['Id']
        reponse = sf.bulk.Lignes_commande__c.upsert(insertions,'Index_STOCKX__c')#%clef,insertions[clef], raw_response=True)
        i+=1
    except SalesforceMalformedRequest as err :
            print(err)
    for clef in deletions.keys():
        try:
            lc =  sf.Lignes_commande__cget_by_custom_id('Index_STOCKX__c', clef)
            reponse =sf.Lignes_commande__c.delete(lc['Id'])
    sendmail(now,summary)
    
    
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
    process(compactDate,now) 
