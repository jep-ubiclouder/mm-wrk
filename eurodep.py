#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 11 juillet 2017

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
from ftplib import FTP, all_errors

import codecs
import os.path
import csv

import pprint

def tr(s):
    return '<tr>%s</tr>\n' % s


def td(arr):
    ligne = ''
    for s in arr:
        ligne += '<td>%s</td>' % s
    return ligne


def th(arr):
    ligne = ''
    for s in arr:
        ligne += '<th>%s</th>' % s
    return ligne


def maketable(clefs, dico, entetes):
    """ Renvoie une table propre HTML pour inclusion dans le mail resultant"""
    result = ''
    if len(clefs) < 1:
        return 'Vide'
    ent = entetes.values()
    result += tr(th(ent))
    for inconnu in clefs:
        result += tr(td([dico[inconnu][0][k] for k in entetes.keys()]))
    return result


def getfromFTP(compactDate):
    """ 
    Telecharge le fichier du jour de la date passée en parammètre format YYYYMMDD
    Renvoie le nom du fichier ecrit sur le disque ou False si une erreur est survenue
    """
    eurodep = FTP(host='ftp.eurodep.fr', user='HOMMEDEFER', passwd='lhdf515')
    try:
        truc = eurodep.nlst('*%s.csv' % compactDate)
    except all_errors as e:
        print('No File today')
        return False

    for t in truc:
        eurodep.retrbinary('RETR %s' % t, open('%s' % t, 'wb').write)
    return truc[0]
def envoieEmailAnomalieProduit(Liste):
    import smtplib
    ''' Envoie une liste des anomalie de EAN survenues lors de l'import Eurodep'''
    ## [r['EAN ART'],r['DES'],r['NOFAC'],r['LIGNE FAC']]
    texteHTML="""
    Bonjour,<br/>
    Voici une liste des anomalies en rapport aux Codes EAN survenus lors de l'importaion EURODEP de ce jour.<br/>
    Le rattachement sera effectué une fois par heure entre 9 heures du matin et 14 heures tout les jours<br/>
    """
    tableau = '''<table>
    <tr><th>Code Eurodep </th><th> Description </th><th> Facture </th><th> Ligne  </th></tr>'''
    for r in Liste:
        record =  "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r[0],r[1],r[2],r[3])
        tableau += record
    tableau +='</table>'
    texteHTML += tableau
    
    
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Compte Inconnus'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com, LBRONNER@homme-de-fer.com'
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    
    
def envoieEmailCI(clientsInconnus):
    ''' Envoie une liste de compte qui ont un code EURODEP mais qui ne sont pas trouvé cette clef dans Salesforce'''
    import smtplib
    # [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
    texteHTML= """
    Bonjour,<br/>
    Voici une liste des clients présents dans le fichier EURODEP que je n'ai pas pu trouver dans SalesForce.<br/>
    Pouvez-vous les créer ou attacher le code Eurodep dans leur fiche, afin que je puisse ratacher les commandes.<br/>
    Le rattachement sera effectué une fois par heure entre 9 heures du matin et 14 heures tout les jours<br/>
    """  
    tableau = '''<table>
    <tr><th>Code Eurodep </th><th> Nom </th><th> Adresse </th><th> Code Postal </th><th> Ville</th></tr>'''
    for k in clientsInconnus.keys():
        r=clientsInconnus[k]
        record =  "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(r[0],r[1],r[2],r[3],r[4])
        tableau += record
    tableau +='</table>'
    texteHTML += tableau
    
    
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Compte Inconnus'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com, LBRONNER@homme-de-fer.com'
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    

def processFile(fname):

    # instanciation de l'objet salesforce
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    # initialisation des divers tableau pour filtrage
    codes_cli = []
    eans = []
    arts = []
    connus = []

    byCODCLI = {}
    byEAN = {}
    byACL = {}
    entetesClientsInconnus = {'NOM': 'Nom', 'ADRESSE': 'Adresse', 'CP': 'Code postal', 'VILLE': 'Ville', 'CODCLI': 'Code EURODEP'}

    # Eurodep ne fournit pas les fichier en UTF-8 !, je m'en occupe moi meme
    sourceEncoding = "iso-8859-1"
    source = fname
    BLOCKSIZE = 1048576  # or some other, desired size in bytes
    with codecs.open(fname, "r", sourceEncoding) as sourceFile:
        with codecs.open("./work.txt", "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)
    # Je travaille dans le fichier temporaire qui en UTF8
    dujour=[]
    with open("./work.txt", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        # dans chaque ligne je repère le champ clef
        for row in reader:
            dujour.append(row)
            # CODCLI est le numero EURODEP
            if row['CODCLI'] not in codes_cli:
                codes_cli.append("%s" % row['CODCLI'])
                byCODCLI[row['CODCLI']] = []
            # ART est le code ACL
            if row['ART'] not in arts:
                arts.append(row['ART'])
                byACL[row['ART']] = []
            # EAN
            if row['EAN ART'] not in eans:
                eans.append(row['EAN ART'])
                byEAN[row['EAN ART']] = []
            # je popule les divers dictionnaires
            byCODCLI[row['CODCLI']].append(row)
            byEAN[row['EAN ART']].append(row)
            byACL[row['ART']].append(row)
            
    # print(codes_cli)

    qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join([
        "\'%s\'" % c for c in codes_cli]) + ')'
    print(qry_code_eurodep)
    les_ids = sf.query(qry_code_eurodep)
    byEurodep = {}
    byEAN = {}
    #byACL = {}
    for acc in les_ids['records']:
        print(acc)
        connus.append(acc['Code_EURODEP__c'])
        byEurodep[acc['Code_EURODEP__c']] = acc['Id']
    ## clientsInconnus = findUnknownItems(connus, codes_cli)
    print(byEurodep)
    oldEurodep000 =[]
    for c in codes_cli :
        ## print(c)
        if c not in byEurodep.keys():
            oldEurodep000.append(c[:-3]+'000')
    if len(oldEurodep000)>0:        
        qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join([
            "\'%s\'" % c for c in oldEurodep000]) + ')'
    
        les_ids = sf.query(qry_code_eurodep)
        for acc in les_ids['records']:
            print(acc)
            connus.append(acc['Code_EURODEP__c'][:-3]+'515')
            byEurodep[acc['Code_EURODEP__c'][:-3]+'515'] = acc['Id']
 
    qry_code_byEAN = 'select id,name,EAN__C from Product2 where EAN__c  in ('+','.join([
        "\'%s\'" % c for c in eans]) + ')'
    
    les_codes_produits = sf.query(qry_code_byEAN)
    for acc in les_codes_produits['records']:
        byEAN[acc['EAN__c']] = acc['Id'] 
    print(byEAN)
    
    CompteInconnus  = {}
    EANInconnus = []
    
    for r in dujour:
    # print(r)
        if r['CODCLI'] in byEurodep.keys(): 
            if r['EAN ART'] in byEAN.keys():
                tmp ={}
                tmp['Facture__c']=r['NOFAC']
                tmp['Bon_de_livraison__c']=r['NOCDE']
                tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
                tmp['Prix_Brut__c'] = r['PBRUT']
                tmp['Quantite__c'] = r['QTE']
                tmp['Prix_Net__c'] = r['PNET']
                tmp['Produit__c'] = byEAN[r['EAN ART']]
                tmp['Quantite__c'] = r['QTE']
                tmp['Ligne__c'] = r['LIGNE FAC']
                tmp['Compte__c'] =  byEurodep[r['CODCLI']]
                
                keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
                
                ## print(tmp)
                try:
                    sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
                except all_errors as e:
                    print(e)
            else:
                tmp ={}
                tmp['Facture__c']=r['NOFAC']
                tmp['Bon_de_livraison__c']=r['NOCDE']
                tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
                tmp['Prix_Brut__c'] = r['PBRUT']
                tmp['Quantite__c'] = r['QTE']
                tmp['Prix_Net__c'] = r['PNET']
                tmp['Code_EAN_EURODEP__c'] = r['EAN ART']
                tmp['Quantite__c'] = r['QTE']
                tmp['Ligne__c'] = r['LIGNE FAC']
                tmp['Code_Client_EURODEP__c'] =  r['CODCLI']
                
                keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
                try:
                    sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
                except all_errors as e:
                    print(e)
                
                EANInconnus.append([r['EAN ART'],r['DES'],r['NOFAC'],r['LIGNE FAC']])
                    
                        
        else:
            tmp ={}
            tmp['Facture__c']=r['NOFAC']
            tmp['Bon_de_livraison__c']=r['NOCDE']
            tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
            tmp['Prix_Brut__c'] = r['PBRUT']
            tmp['Quantite__c'] = r['QTE']
            tmp['Prix_Net__c'] = r['PNET']
            tmp['Code_EAN_EURODEP__c'] = r['EAN ART']
            tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['LIGNE FAC']
            tmp['Code_Client_EURODEP__c'] =  r['CODCLI']
            
            keyforupsert = r['NOFAC'] + str(r['LIGNE FAC'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            if  r['CODCLI'] not in CompteInconnus.keys():
                CompteInconnus[r['CODCLI']] = [r['CODCLI'],r['NOM'],r['ADRESSE'],r['CP'],r['VILLE']]
                    
    print(EANInconnus)
    print(CompteInconnus)
    pathFile = './ComptesInconnus.txt'
    cpteDump =  open(pathFile,'a')
    for k in CompteInconnus.keys():
        cpteDump.write(CompteInconnus[k][0] + '\n')
    cpteDump.close()
    ## TODO
    ## Dump les CompteInconnus dans un fichier COMPTESINCONNU a la fin
    envoieEmailCI(CompteInconnus)
    envoieEmailAnomalieProduit(EANInconnus)
def TryConnectComptes():
    pass
    pathFile = './ComptesInconnus.txt'
    cpteDump = open(pathFile,'r')
    ComptesInconnus =[]
    for l in cpteDump.readlines():
        id=l[:-1] 
        if id not in ComptesInconnus:
            ComptesInconnus.append(id)
    if len(ComptesInconnus)>0:
        sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
        qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join(["\'%s\'" % c for c in ComptesInconnus]) + ')'
        result = sf.query(qry_code_eurodep)
        records =  result['records']
        if len(records)>0:
            bulkUpdates= []
            for r in records:
                AccId = r['Id']
                qryUpdateLignes = ' select id, Ligne__c, Code_Client_EURODEP__c,Compte__c from Commande__c where  Code_Client_EURODEP__c=\'%s\' '%r['Code_EURODEP__c']
                resUpdate = sf.query(qryUpdateLignes)
                for rec in resUpdate['records']:
                    bulkUpdates.append({'Id': rec['Id'],'Compte__c':AccId})
            sf.bulk.update(bulkUpdates)
    cpteDump.close() 

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")
    parser.add_argument('-r', '--reconnect', action='store_true', default=False)
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
        
    if args.reconnect is None or args.reconnect == False:
        compactDate = '%s%02i%02i' % (now.year, now.month, now.day)
        fn = getfromFTP(compactDate)
        if fn != False:
            processFile(fn)
    else:
        TryConnectComptes()
        