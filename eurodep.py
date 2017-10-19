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


def envoieEmail(clientsInconnus, produitsInconnus):

    pass


def findUnknownItems(connus, fournis):
    """
    renvoie un tableau des elements de fournis qui ne sont pas connus
    """
    resultat = []
    for k in fournis:
        if k not in connus:
            resultat.append(k)
    return resultat


def findProduitsInconnus(ean, acl, EANInconnus, ACLInconnus):
    """
    cherche si on arrive a retrouver les EANn par des acl ou reciproquement
    """
    produitsInconnus = []
    for k in EANInconnus:
        if ean[k][0]['ART'] not in acl.keys():
            produitsInconnus.append(ean[k])
        else:
            print('found unkown EAN k', k, 'by', ean[k][0]['ART'])

    for k in ACLInconnus:
        if acl[k][0]['EAN ART'] not in ean.keys():
            produitsInconnus.append(acl[k])
        else:
            print('found unkown ACL k', k, 'by', acl[k][0]['EAN ART'])
    return produitsInconnus


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
    qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (' + ','.join([
        "\'%s\'" % c for c in codes_cli]) + ')'

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
    qry_code_eurodep = 'select id,name,ShippingCity,Code_EURODEP__c from account where Code_EURODEP__c in (' + ','.join([
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
    EANInconnus = {}
    
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
                keyforupsert = r['NOFAC'] + str(r['NOFAC'])
                ## print(tmp)
                try:
                    sf.Commande__c.upsert('key4upsert__c/%s' % keyforupsert, tmp, raw_response=True)
                except all_errors as e:
                    print(e)
            else:
                if r['EAN ART'] not in EANInconnus.keys():
                        EANInconnus[r['EAN ART']] = [r['EAN ART'],r['DES']]
        else:
            if  r['CODCLI'] not in CompteInconnus.keys():
                CompteInconnus[r['CODCLI']] = [r['CODCLI'],r['NOM'],r['ADRESSE']]
                    
    print(EANInconnus)
    print(CompteInconnus)
    
    '''eurodep_inconnus =[]
    
    for k in byCODCLI.keys():  ## je cherche les codes EURODEP qui ne sont pas dans SF 
        if k not in connus:
            #for r in byCODCLI[k]:
            eurodep_inconnus.append(byCODCLI[k])
        
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(eurodep_inconnus)
    # sys.exit()
    
    connus = []
    qry_eans = 'select id,name,Code_ACL__c,EAN__c from product2 where EAN__c in (' + ','.join([
        "\'%s\'" % c for c in eans]) + ')'
    les_eans = sf.query(qry_eans)
    for prod in les_eans['records']:
        # print("EAN",prod)
        connus.append(prod['EAN__c'])
        #byEAN[prod['EAN__c']] = prod['Id']
    EANInconnus = findUnknownItems(connus, eans)

    connus = []
    qry_arts = 'select id,name,Code_ACL__c,EAN__c from product2 where Code_ACL__c in (' + ','.join([
        "\'%s\'" % c for c in arts]) + ')'
    les_Acl = sf.query(qry_arts)

    for prod in les_Acl['records']:
        connus.append(prod['Code_ACL__c'])
        #byACL[prod['Code_ACL__c']] = prod['Id']
    ACLInconnus = findUnknownItems(connus, arts)
    # sf.Contact.update('003e0000003GuNXAA0',{'LastName': 'Jones', 'FirstName': 'John'})
    
    
    
    ## sf.Commande__c.insert({})
    produitsInconnus = findProduitsInconnus(byEAN, byACL, EANInconnus, ACLInconnus)
    # print("Client Inconnus", clientsInconnus, "\nean inconnus", EANInconnus, "\nACL Inconnus", ACLInconnus, "\nProduits Inconnus", produitsInconnus)
    ## print(maketable(clientsInconnus, byCODCLI, entetesClientsInconnus))
    
    
    
    for r in dujour:
        # print(r)
        tmp ={}
        tmp['Facture__c']=r['NOFAC']
        tmp['Bon_de_livraison__c']=r['NOCDE']
        tmp['Date_de_commande__c']='-'.join((r['DATFAC'][:4],r['DATFAC'][4:6],r['DATFAC'][6:]))
        tmp['Prix_Brut__c'] = r['PBRUT']
        tmp['Quantite__c'] = r['QTE']
        tmp['Prix_Net__c'] = r['PNET']
        tmp['Produit__c'] = r['ART']
        tmp['Quantite__c'] = r['QTE']
        tmp['Ligne__c'] =r['LIGNE FAC']
        keyforupsert__c = r['NOFAC'] + str(r['NOFAC'])

        try:
            sf.Commande__c.upsert('key4upsert__c/%s' % keyforupsert__c, tmp, raw_response=True)
        except all_errors as e:
            print(e)'''
        

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")

    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
        
    
    compactDate = '%s%02i%02i' % (now.year, now.month, now.day)
    fn = getfromFTP(compactDate)
    if fn != False:
        processFile(fn)
