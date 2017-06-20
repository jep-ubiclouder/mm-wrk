#!/usr/bin/python3.4
#-*- coding: utf-8 -*-

'''
Created on 8 juin 2017

@author: jean-eric preis
'''
from simple_salesforce import Salesforce
import sys

def sendmail(nbreIns,nbreUpd):

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
        Lignes modifiées: %s
    </p>
  </body>
</html>
""" %(nbreIns,nbreUpd)
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    
    
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'resultat du jour'
    msg['From'] = ubunutu@localhost
    msg['To'] = jean-eric.preis@ubiclouder.com
    
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


sf = Salesforce(username='jep@assembdev.com', password='ubi$2017', security_token='aMddugz7oc45l1uhqWAE308Z', sandbox=True)

toto = sf.query('select id from Lignes_commande__c')
""" for r in toto['records']:
    id=r['Id']
    print( 'deleting ',id)
    sf.Lignes_commande__c.delete(id)
while 'nextRecordUrl' in toto.keys():
    toto = sf.query_more(toto['nextRecordUrl'])
    for r in toto['records']:
        id=r['Id']
        print( 'deleting ',id)
        sf.Lignes_commande__c.delete(id) """
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
updates =[]
insertions =[]
effaces =[]
with open('./bucket-mm-daily/EXPORT_20170619.CSV', 'r',encoding='utf-8') as csvfile:
    reader=  csv.DictReader(csvfile,delimiter=',')
    for row in reader:
        record={}
        statut = row['STATUT'] 
        commande=row['COMMANDE']
        if commande=='123456':continue
        for clef in row.keys():
            if clef in mapFields.keys():
                # print(clef,row[clef])
                if clef=='DATE_CDE' or clef == 'PARUTION':
                    print(clef, row[clef])
                    
                    (d,m,a) = row[clef].split('-')
                    value= '%s-%s-%s'%(a,m,d)
                    row[clef]=value
                    
                try: 
                    record[mapFields[clef]]=row[clef]
                except :
                    print('ooops')
        try:
            #print( record)
            if statut =='M': updates.append(record)
            elif statut=='C': insertions.append(record)
            elif statut =='D':effaces.append(record)
            # reponse = sf.Lignes_commande__c.create(record)
            pass
        except :
           continue
        i += 1
        # if i > 30:
        #    break
    print(insertions)
    print(updates)    
    sendmail(len(insertions),len(updates))
    
if __name__ == '__main__':
    pass
