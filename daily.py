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


def getCredentials(isTest):
    from cryptography.fernet import Fernet
    clef = b'y1RrSzZel5RRjMjCZwwLVnVppKzqHQT0v-Mm96WNdS4='
    dataTest = b'gAAAAABZqXG7ztOFfBzQyWInJBGi2ug_TnFsZFLM0fbCCx6POD8ki_qCJRIlIm8jBh9Z918JxLi3He-46-rcoIZ_BgrwD9VvdYRA5_6G5k8FySU0m7qpPnV6UDh6ayqPlR-mvo8Dp3DTi8xElZVhp2tKtZBL95tl-5e2XtNsz67D1lkHui856v2G5jTh6zYNMS3ifjvnl1DQ0SuEKZ2FZay031QRu1q7Wg=='
    dataProd = b'gAAAAABZu4MLAoZXiIJnPwf-pn59_WKdt18um9Pn6K2AKOhT62GUsCXyDlFo4ArqrOnB08fL4p3ZJosIorRbllXa0mqOQiDTc7Bwv2Xneg3_UlN3z5hxR3sc8D2wNNiPcpoy3ofnr43e403TWulo60FOOAKr7mfWJSL8IpepcPVOWhv9CLltgvMHjqtmzJO621gKAtpuW2uYwv5dWx_VQXvSdDpoyl0SKw=='
    if isTest:
        data = dataTest
    else:
        data = dataProd
    import json
    cipher = Fernet(clef)
    creds = json.loads(cipher.decrypt(data).decode())
    creds =  {'user':'hp@maisonmoderne.lu', 'passwd':'ubiClouder$2018','security_token':'ImLyrZrrANcN70V8S4N3vR6YJ'}
    return creds


def tr(s):
    return '<tr>%s</tr>' % s


def td(arr):
    ligne = ''

    for s in arr:
        ligne += '<td>%s</td>' % s
    # print(ligne)

    return ligne


def maketable(summary):
    if len(summary) <= 0:
        return 'Vide'
    table = ''
    liste = []
    orderedList = []
    for k in summary.keys():
        orderedList.append(k)
    orderedList.sort()
    for clef in orderedList:
        liste = []
        liste.append(clef)
        try:
            liste.append(summary[clef]['NOM__c'])
        except KeyError:
            liste.append('Nom Inconnu')
        try:
            liste.append(summary[clef]['COMMANDE_STX__c'])
        except KeyError:
            liste.append('Commande Inconnu')
        try:
            liste.append(summary[clef]['Brut_Total__c'])
        except KeyError:
            liste.append('Montant Inconnu')
        try:
            liste.append(summary[clef]['DATE_CDE__c'])
        except KeyError:
            liste.append('1')
        table += tr(td(liste))
    return table


def sendmail(now, summary, errors, fullUpdate, no_op, isTest):
    import smtplib

    html = """\
<html>
  <head></head>
  <body>
    <p>Bonjour Mirella !<br>
        Voici les resultats du batch pour la date:%s<br>
        <i>Enregistrements acceptés<i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Date Commande</th></tr>
        %s
        </table>
        <i>Enregistrements signalés modifiés dans Stock_X, donc effacés et remplacés intégralement</i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Date Commande</th></tr>
        %s
        </table>
        
    </p>
  </body>
</html>
""" % ('%02i-%02i-%s' % (now.day, now.month, now.year), maketable(summary), maketable(no_op))
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    if isTest:
        msg['Subject'] = 'resultat du jour SANDBOX'
        msg['From'] = 'lignesdecommandes@mm-aws.com'
        msg['To'] = 'jean-eric.preis@ubiclouder.com'
    else:
        msg['Subject'] = 'resultat du jour'
        msg['From'] = 'lignesdecommandes@mm-aws.com'
        msg['To'] = 'jean-eric.preis@ubiclouder.com, mirella.ciszewski@maisonmoderne.com, projets@ubiclouder.com'
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def findFile(parmDate):

    base = './bucket-mm-daily/EXPORT_%s.CSV' % parmDate
    return base


def sendErrorMail():
    import smtplib
    html = """\
<html>
  <head></head>
  <body>
    <p>Bonjour !<br>
        Je ne suis pas arrivé à me connecter sur l'org de production de maison moderne avec le login <b> conrad.heron@maisonmoderne.lu </b>
        Veuillez verifier le mot de passe et le token de sécurité et prévenez Jean eric pour qu'il adapte le script. 
        Bien à vous,
        Votre bot préféré !
    </p>
  </body>
</html>
"""
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'Erreur de connection'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com, marie-noelle.marx@maisonmoderne.com, hp@ubiclouder.com, ea@ubiclouder.com'

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def process(parmDate, now, isTest):

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

    creds = getCredentials(isTest)

    try:
        sf = Salesforce(username=creds['user'], password=creds['passwd'], security_token=creds['security_token'], sandbox=isTest)
    except Exception as err:
        sendErrorMail()
        import sys
        sys.exit()

    import os.path
    import csv
    mapFields = {}
    mapfile = open('./bucket-mm-daily/mapping_lignes-de-commandes2017.sdl', 'r')
    for l in mapfile.readlines():
        if l[0] == '#':
            continue
        (clefSTX, clefSF) = l.split('=')
        mapFields[clefSTX] = clefSF[:-1]
    # print(mapFields)
    i = 0
    updates = {}
    insertions = {}
    deletions = []
    deleteFactures =[]
    lstCLients = []
    errors = {}
    no_op = {}
    with open(findFile(parmDate), 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            inserer = False
            record = {}
            statut = row['STATUT']
            commande = row['COMMANDE']

            # clients uniques
            clientStx = row['CLIENT']
            action = row['STATUT']
            if action == 'S':
                if row['COMMANDE'] not in deletions:
                    deletions.append(row['COMMANDE'])
                    deleteFactures.append(row['COMMANDE'])
                continue
            Index_STOCKX__c = row['IND']
            for clef in row.keys():
                if clef == 'IND':
                    continue
                    # Nous faisons des upsert sur le champ Index_STOCKX__c NE DOIT PAS apparraitre dans le record
                if clef in mapFields.keys():
                    if clef == 'DESIGNATION':
                        row[clef] = row[clef][:80]

                    # passage en AA-MM-JJ
                    if clef == 'DATE_CDE' or clef == 'PARUTION':
                        ## print(clef, row[clef])
                        (d, m, a) = row[clef].split('-')
                        value = '%s-%s-%s' % (a, m, d)
                        row[clef] = value
                    try:
                        record[mapFields[clef]] = row[clef]
                    except:
                        print('ooops')
            if action == 'M':  # une modification
                if row['COMMANDE'] not in deletions:
                    deletions.append(row['COMMANDE'])
                inserer = True
                no_op[Index_STOCKX__c] = record

            try:
                if action == 'C':
                    
                    insertions[Index_STOCKX__c] = record
                    # deletions[Index_STOCKX__c] = record
                elif action == 'S':
                    ## if row['COMMANDE'] not in deletions:
                    ##    deletions.append(row['COMMANDE'])
                    pass  # deletions[Index_STOCKX__c] = record
                elif action == 'M' and inserer == False:
                    no_op[Index_STOCKX__c] = record

            except Exception as err:
                print('Erreur', err)
        i = 1
    summary = {}
    
    if len(deletions)>0:
        lstCommandesToBeDel = ""
        for comm in deletions:
            lstCommandesToBeDel += "'%s'," % comm
        qryForIDtoBEDel = "select id from Lignes_commande__c where COMMANDE_STX__c in (%s)" % lstCommandesToBeDel[:-1]  # on omet la derniere virgule !!
        print(qryForIDtoBEDel)
        
        rex = sf.query(qryForIDtoBEDel)
        tobedel = []
        for r in rex['records']:
            # print(rex)
            tobedel.append({'Id': r['Id']})
        if len(tobedel) > 0:
            resDel = sf.bulk.Lignes_commande__c.delete(tobedel)
        
    for comm in deleteFactures:
        lstCommandesToBeDel += "'%s'," % comm    
    qryForDeleteCommandes = "select id from Commandes__c where Commande_STX__c in (%s)" % lstCommandesToBeDel[:-1]
    rex = sf.query(qryForDeleteCommandes)
    tobedel = []
    for r in rex['records']:
        # print(rex)
        tobedel.append({'Id': r['Id']})
    if len(tobedel) > 0:
        resDel = sf.bulk.Commandes__c.delete(tobedel)
    #qryForIDtoBEDel = "select id from commande__c where COMMANDE_STX__c in (%s)" % lstCommandesToBeDel[:-1]  # on omet la derniere virgule !!
    
    
    fullUpdate = {}
    for clef in insertions.keys():
        try:
            ccstx = insertions[clef]['Cle_Client_STX__c']
            # print(insertions[clef])
            if ccstx not in summary.keys():
                summary[ccstx] = {'COMMANDE_STX__c': '', 'lignes': 0, 'Brut_Total__c': 0.00, 'NOM__c': ''}
            summary[ccstx]['COMMANDE_STX__c'] = insertions[clef]['COMMANDE_STX__c']
            summary[ccstx]['lignes'] += 1
            summary[ccstx]['Brut_Total__c'] += float(insertions[clef]['Brut_Total__c'])
            summary[ccstx]['NOM__c'] = insertions[clef]['NOM__c']
            summary[ccstx]['NOM__c'] = insertions[clef]['DATE_CDE__c']
        except Exception as err:
            print('exception', err)
        try:
            reponse = sf.Lignes_commande_Import__c.upsert('Index_STOCKX__c/%s' % clef, insertions[clef], raw_response=True)
            # print(reponse,insertions[clef])
        except Exception as err:
            print(err)
            errors[clef] = insertions[clef]
    for clef in no_op.keys():
        try:
            ccstx = no_op[clef]['Cle_Client_STX__c']
            # print(insertions[clef])
            if ccstx not in summary.keys():
                fullUpdate[ccstx] = {'COMMANDE_STX__c': '', 'lignes': 0, 'Brut_Total__c': 0.00, 'NOM__c': ''}
            fullUpdate[ccstx]['COMMANDE_STX__c'] = no_op[clef]['COMMANDE_STX__c']
            fullUpdate[ccstx]['lignes'] += 1
            fullUpdate[ccstx]['Brut_Total__c'] += float(no_op[clef]['Brut_Total__c'])
            fullUpdate[ccstx]['NOM__c'] = no_op[clef]['NOM__c']
        except Exception as err:
            print('exception', err)
        try:

            reponse = sf.Lignes_commande_Import__c.upsert('Index_STOCKX__c/%s' % clef, no_op[clef], raw_response=True)
            # print(reponse,insertions[clef])
        except Exception as err:
            print(err)
            errors[clef] = insertions[clef]

    sendmail(now, insertions, errors, fullUpdate, no_op, isTest)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('-d', '--date', action="store", dest="parmDate")
    parser.add_argument('-t', '--test', action='store_true', default=False)
    args = parser.parse_args()
    from datetime import datetime, timedelta
    if args.parmDate:
        now = datetime.strptime(args.parmDate, '%Y-%m-%d')
    if args.parmDate is None:
        now = datetime.now() - timedelta(days=1)
    compactDate = '%s%02i%02i' % (now.year, now.month, now.day)

    if args.test is None or args.test == False:
        isTest = False
    else:
        isTest = True

    process(compactDate, now, isTest)
