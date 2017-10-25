#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 24/10/2017

@author: jean-eric preis
'''
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
    
    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'EAN Inconnus'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com'
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    print('Email EAN envoyé')
    
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
    
    print(texteHTML)
    from email.mime.text import MIMEText
    msg = MIMEText(texteHTML, 'html')
    msg['Subject'] = 'Compte Inconnus'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com'
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    print('Email Comptes envoyé')

def processFile():

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
    '''
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
    '''
    # Je travaille dans le fichier temporaire qui en UTF8
    dujour=[]
    with open("./complement2017.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        # dans chaque ligne je repère le champ clef
        for row in reader:
            dujour.append(row)
            # CODCLI est le numero EURODEP
            if row['code client Eurodep'] not in codes_cli:
                codes_cli.append("%s" % row['code client Eurodep'])
                byCODCLI[row['code client Eurodep']] = []
            # ART est le code ACL
            #if row['ART'] not in arts:
            #    arts.append(row['ART'])
            #    byACL[row['ART']] = []
            # EAN
            if row['Code Ean'] not in eans:
                eans.append(row['Code Ean'])
                byEAN[row['Code Ean']] = []
            # je popule les divers dictionnaires
            byCODCLI[row['code client Eurodep']].append(row)
            byEAN[row['Code Ean']].append(row)
            #byACL[row['ART']].append(row)
            
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
        if r['Code Ean'] in byEAN.keys() and r['code client Eurodep'] in byEurodep.keys():
            tmp ={}
            tmp['Facture__c']=r['nofac']
            tmp['Bon_de_livraison__c']=r['bl']
            tmp['Date_de_commande__c']='-'.join((r['datfac'][-4:],r['datfac'][3:5],r['datfac'][:2]))
            tmp['Prix_Brut__c'] = ''.join('.'.join(r['pbrut'].split(',')).split(' '))
            tmp['Quantite__c'] = ''.join('.'.join(r['QTE'].split(',')).split(' '))
            tmp['Prix_Net__c'] = ''.join('.'.join(r['prinet'].split(',')).split(' '))
            tmp['Produit__c'] = byEAN[r['Code Ean']]
            # tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['ligne']
            tmp['Compte__c'] =  byEurodep[r['code client Eurodep']]
            
            keyforupsert = r['nofac'] + str(r['ligne'])
            
            ## print(tmp)
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
        elif r['Code Ean'] not in byEAN.keys() and r['code client Eurodep'] in byEurodep.keys():
            tmp ={}
            tmp['Facture__c']=r['nofac']
            tmp['Bon_de_livraison__c']=r['bl']
            tmp['Date_de_commande__c']='-'.join((r['datfac'][-4:],r['datfac'][3:5],r['datfac'][:2]))
            tmp['Prix_Brut__c'] = ''.join('.'.join(r['pbrut'].split(',')).split(' '))
            tmp['Quantite__c'] = ''.join('.'.join(r['QTE'].split(',')).split(' '))
            tmp['Prix_Net__c'] = ''.join('.'.join(r['prinet'].split(',')).split(' '))
            # tmp['Code_EAN_EURODEP__c'] = r['Code Ean']
            # tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['ligne']
            tmp['Produit__c'] = byEAN[r['Code Ean']]
            tmp['Code_Client_EURODEP__c'] =  r['code client Eurodep']
            
            keyforupsert = r['nofac'] + str(r['ligne'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            
            EANInconnus.append([r['Code Ean'],r['des'],r['nofac'],r['ligne']])
                
                    
        elif r['Code Ean'] in byEAN.keys() and r['code client Eurodep'] not in byEurodep.keys():
            tmp ={}
            tmp['Facture__c']=r['nofac']
            tmp['Bon_de_livraison__c']=r['bl']
            tmp['Date_de_commande__c']='-'.join((r['datfac'][-4:],r['datfac'][3:5],r['datfac'][:2]))
            tmp['Prix_Brut__c'] = ''.join('.'.join(r['pbrut'].split(',')).split(' '))
            tmp['Quantite__c'] = ''.join('.'.join(r['QTE'].split(',')).split(' '))
            tmp['Prix_Net__c'] = ''.join('.'.join(r['prinet'].split(',')).split(' '))
            tmp['Code_EAN_EURODEP__c'] = r['Code Ean']
            # tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['ligne']
            tmp['Compte__c'] =  byEurodep[r['code client Eurodep']]
            # tmp['Code_Client_EURODEP__c'] =  r['code client Eurodep']
            
            keyforupsert = r['nofac'] + str(r['ligne'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            if  r['code client Eurodep'] not in CompteInconnus.keys():
                 CompteInconnus[r['code client Eurodep']] = [r['code client Eurodep'],r['nom'],r['adresse'],r['cp'],r['ville']]
        else: 
            tmp ={}
            tmp['Facture__c']=r['nofac']
            tmp['Bon_de_livraison__c']=r['bl']
            tmp['Date_de_commande__c']='-'.join((r['datfac'][-4:],r['datfac'][3:5],r['datfac'][:2]))
            tmp['Prix_Brut__c'] = ''.join('.'.join(r['pbrut'].split(',')).split(' '))
            tmp['Quantite__c'] = ''.join('.'.join(r['QTE'].split(',')).split(' '))
            tmp['Prix_Net__c'] = ''.join('.'.join(r['prinet'].split(',')).split(' '))
            tmp['Code_EAN_EURODEP__c'] = r['Code Ean']
            # tmp['Quantite__c'] = r['QTE']
            tmp['Ligne__c'] = r['ligne']
            tmp['Code_Client_EURODEP__c'] =  r['code client Eurodep']
            
            keyforupsert = r['nofac'] + str(r['ligne'])
            try:
                sf.Commande__c.upsert('ky4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
            except all_errors as e:
                print(e)
            if  r['code client Eurodep'] not in CompteInconnus.keys():
                 CompteInconnus[r['code client Eurodep']] = [r['code client Eurodep'],r['nom'],r['adresse'],r['cp'],r['ville']]            
    print(EANInconnus)
    print(CompteInconnus)
    pathFile = './ComptesInconnusHisto.txt'
    cpteDump =  open(pathFile,'a')
    for k in CompteInconnus.keys():
        cpteDump.write(CompteInconnus[k][0] + '\n')
    cpteDump.close()
    ## TODO
    ## Dump les CompteInconnus dans un fichier COMPTESINCONNU a la fin
    if len(CompteInconnus.keys())>0:
        envoieEmailCI(CompteInconnus)
    if len(EANInconnus)>0:
        envoieEmailAnomalieProduit(EANInconnus)
def TryConnectComptes():
    pathFile = './ComptesInconnusHisto.txt'
    stackTrouves =[]
    cpteDump = open(pathFile,'r')
    ComptesInconnus =[]
    Original = []
    for l in cpteDump.readlines():
        id=l[:-1] 
        racine=id[:-3]
        if id not in Original:
            Original.append(id)
            ComptesInconnus.append(racine+'000')
            ComptesInconnus.append(racine+'515')
    if len(ComptesInconnus)>0:
        sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
        qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (\'PLACEHOLDER\',' + ','.join(["\'%s\'" % c for c in ComptesInconnus]) + ')'
        result = sf.query(qry_code_eurodep)
        records =  result['records']
        stackTrouves =[]
        if len(records)>0:
            bulkUpdates= []
            for r in records:
                AccId = r['Id']
                qryUpdateLignes = ' select id, Ligne__c, Code_Client_EURODEP__c,Compte__c from Commande__c where  Code_Client_EURODEP__c=\'%s\' '%r['Code_EURODEP__c']
                resUpdate = sf.query(qryUpdateLignes)
                
                for rec in resUpdate['records']:
                    bulkUpdates.append({'Id': rec['Id'],'Compte__c':AccId})
                    if rec['Code_Client_EURODEP__c'][:-3] not in stackTrouves:
                        stackTrouves.append(rec['Code_Client_EURODEP__c'][:-3])                    
            print(bulkUpdates)
            if(len(bulkUpdates))>0:
                sf.bulk.Commande__c.update(bulkUpdates)
    cpteDump.close()
    
    cpteDump = open(pathFile,'w')
    for s in Original:
        if s[:-3] not in stackTrouves:
            cpteDump.write(s+'\n')
    cpteDump.close()
    print('reconcilé')
    print(bulkUpdates)

if __name__ == '__main__':
    processFile()
        

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

sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')

qryAllContact = 'select id,Fonction__c,Title,Service__c,Services__c from Contact'

lesContacts = sf.query_all(qryAllContact)
recs = lesContacts['records']
print(len(recs))

updates=[]
i=1
for r in recs:
    updates.append({'Id':r['Id'],'Fonction__c':r['Title']})
    i += 1
    if i % 2500 == 0:
        result =sf.bulk.Contact.update(updates)
        updates = []
        print(i)
result =sf.bulk.Contact.update(updates)

qryallProducts = "select id,Famille_de_Produit__c,Famille__c from Product2"
qryallFamily = "select id,Code_Famille__c from Famille_de_Produit__c "
lesProduits =les_ids = sf.query(qryallProducts)
lesFamilles =sf.query(qryallFamily)

hFamille = lesFamilles['records']
byCodeFamille = {}
for rec in hFamille:
    byCodeFamille[rec['Code_Famille__c']] =rec['Id']


updateList=[]    
for rProd in lesProduits['records']:
    
    cf = rProd['Famille__c']
    id = rProd['Id']
    if cf in byCodeFamille.keys():
        updateList.append({'Id':id,'Famille_de_Produit__c':byCodeFamille[cf]})
    else:
        print('pas trouve',cf)
        
if len(updateList)>0:
    print(sf.bulk.Product2.update(updateList))
'''