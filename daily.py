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
    return '<tr>%s</tr>' % s


def td(arr):
    ligne = ''

    for s in arr:
        ligne += '<td>%s</td>' % s
    #print(ligne)

    return ligne


def maketable(summary):
    if len(summary) <= 0:
        return 'Vide'
    table = ''
    liste = []
    for clef in summary.keys():
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
            liste.append(summary[clef]['lignes'])
        except KeyError:
            liste.append('1')
        table += tr(td(liste))
    return table


def sendmail(now, summary, errors, deletions,no_op):

    # Import smtplib for the actual sending function
    import smtplib
    # print(summary)
    # Import the email modules we'll need

    html = """\
<html>
  <head></head>
  <body>
    <p>Bonjour Marie-Noëlle !<br>
        Voici les resultats du batch pour la date:%s<br>
        <i>Enregistrements acceptés<i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Lignes</th></tr>
        %s
        </table>
        <i>Enregistrements inchangés pour Salesforce mais peut etre dans stockX</i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Lignes</th></tr>
        %s
        </table>
        <i>Enregistrements rejetés</i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Lignes</th></tr>
        %s
        </table>
        <i>Enregistrements éffacés</i>
        <table>
        <tr><th>Code Ligne STX</th><th>Nom</th><th>Commande</th><th>Montant Brut</th><th>Lignes</th></tr>
        %s
        </table>
        
    </p>
  </body>
</html>
""" % ('%02i-%02i-%s' % (now.day, now.month, now.year), maketable(summary), maketable(no_op),maketable(errors), maketable(deletions))
    from email.mime.text import MIMEText
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'resultat du jour'
    msg['From'] = 'lignesdecommandes@mm-aws.com'
    msg['To'] = 'jean-eric.preis@ubiclouder.com' #, marie-noelle.marx@maisonmoderne.com'

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def findFile(parmDate):

    base = './bucket-mm-daily/EXPORT_%s.CSV' % parmDate
    return base


def process(parmDate, now):

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
    mapfile = open('./bucket-mm-daily/mapping_lignes-de-commandes2017.sdl', 'r')
    for l in mapfile.readlines():
        if l[0] == '#':
            continue
        (clefSTX, clefSF) = l.split('=')
        mapFields[clefSTX] = clefSF[:-1]
    print(mapFields)
    i = 0
    updates = {}
    insertions = {}
    deletions = []
    lstCLients = []
    errors = {}
    no_op ={}
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

            if commande == '123456':
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
                inserer =True
                no_op[Index_STOCKX__c] = record
                '''try:
                    lc = sf.Lignes_commande__c.get_by_custom_id('Index_STOCKX__c', Index_STOCKX__c)
                    for k in record.keys():
                        if k == 'CLIENT_FINAL__c':
                            continue
                        if k in lc.keys():
                            if k in ('Brut_Total__c', 'Brut_Editeur__c'):
                                lc[k] = "%10.2f" % float(lc[k])
                                record[k] = "%10.2f" % float(record[k])

                            if lc[k] != record[k]:  # une difference sur un des champs qui  nous interesse
                                print('InstockX', Index_STOCKX__c, 'key', k, 'lc', lc[k], 'rec', record[k])
                                inserer = True
                                break

                except Exception as err:
                    print(err, Index_STOCKX__c)
                    inserer = True
                    '''
                    
            
            try:
                if action == 'C' :
                    insertions[Index_STOCKX__c] = record
                    # deletions[Index_STOCKX__c] = record
                elif action == 'S':
                    pass ## deletions[Index_STOCKX__c] = record
                elif action == 'M' and inserer == False:
                    no_op[Index_STOCKX__c] = record
                    
            except Exception as err:
                print('Erreur', err)
        i = 1
    summary = {}
    
    
    lstCommandesToBeDel = ""
    for comm in deletions:
        lstCommandesToBeDel += "'%s',"%comm
    qryForIDtoBEDel = "select id from Lignes_commande__c where COMMANDE_STX__c in (%s)" % lstCommandesToBeDel[:-1] # on omet la derniere virgule !! 
    print(qryForIDtoBEDel) 
    rex= sf.query(qryForIDtoBEDel)
    tobedel=[]
    for r in rex['records']:
        print(rex)
        tobedel.append({'Id':r['Id']})
    if len(tobedel)>0:
        resDel = sf.bulk.Lignes_commande__c.delete(tobedel)
        print(resDel)

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
        except Exception as err:
            print('exception', err)
        try:
            reponse = sf.Lignes_commande__c.upsert('Index_STOCKX__c/%s' % clef, insertions[clef], raw_response=True)
            ## print(reponse,insertions[clef])
        except Exception as err:
            print(err)
            errors[clef] = insertions[clef]
    for clef in no_op.keys():
        try:
            ccstx = insertions[clef]['Cle_Client_STX__c']
            # print(insertions[clef])
            if ccstx not in summary.keys():
                summary[ccstx] = {'COMMANDE_STX__c': '', 'lignes': 0, 'Brut_Total__c': 0.00, 'NOM__c': ''}
            summary[ccstx]['COMMANDE_STX__c'] = insertions[clef]['COMMANDE_STX__c']
            summary[ccstx]['lignes'] += 1
            summary[ccstx]['Brut_Total__c'] += float(insertions[clef]['Brut_Total__c'])
            summary[ccstx]['NOM__c'] = insertions[clef]['NOM__c']
        except Exception as err:
            print('exception', err)
        try:
            reponse = sf.Lignes_commangrep 22903-1 de__c.upsert('Index_STOCKX__c/%s' % clef, insertions[clef], raw_response=True)
            ## print(reponse,insertions[clef])
        except Exception as err:
            print(err)
            #errors[clef] = insertions[clef]

    sendmail(now, insertions, errors, deletions,no_op)
    # if len(errors)>0:
    #    sendmailE(now,errors)


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
    process(compactDate, now)
