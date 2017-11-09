#!/usr/local/bin/python3.6
#-*- coding: utf-8 -*-

'''
Created on 07 Novembre 2017

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
import datetime
import csv
def process():
    
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry  ='SELECT id,Bon_de_livraison__c,Code_Client_EURODEP__c,Code_EAN_EURODEP__c,Compte__c,C_A_Brut__c,C_A_Net__c,Date_de_commande__c,Facture__c,Ligne__c,Prix_Brut__c,Prix_Net__c,Produit__c,Quantite__c,Reference_Client__c FROM Commande__c where compte__c = null and Code_Client_EURODEP__c = null  order by Date_de_commande__c desc'
    result = sf.query_all(qry)['records']
    unknownCompteByFacture = {} 
    
    print('ldc trouvées',len(result))
    # Je mets en relation les facture__c et les id SF
    for r in result:
        d = datetime.datetime.strptime(r['Date_de_commande__c'], '%Y-%m-%d').date() + datetime.timedelta(days=1)
        dateclef = d.strftime('%Y%m%d')
        ## print(dateclef,r['Facture__c'],r['Facture__c']+dateclef)
        ## print(r['Facture__c']+dateclef)
        if (r['Facture__c']+dateclef) not in unknownCompteByFacture.keys():
            unknownCompteByFacture[r['Facture__c']+dateclef] = []
            
        unknownCompteByFacture[r['Facture__c']+dateclef].append(r['Id'])
        
    #for k in unknownCompteByFacture.keys():
    #    print(k,unknownCompteByFacture[k])  
    
    allSorifa =[]
    byFacture ={}
    # je relie les factures avec les code SORIFA
    with open('./Internet2017.csv','r') as f: # Internet2017.csv venteshisto.csv
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            # print(l['date mouvement'])
            dateclef='%s%s%s' %(l['date mouvement'][-4:],l['date mouvement'][3:5],l['date mouvement'][:2])
            ## print(dateclef)
            ## print(l['numero document']+dateclef)
            
            if (l['numero document']+dateclef) in unknownCompteByFacture.keys():
                if (l['numero document']+dateclef) not in byFacture.keys():
                    byFacture[l['numero document']+dateclef] = l['Code client sorifa']
                
                if l['Code client sorifa'] not in allSorifa:
                    allSorifa.append(l['Code client sorifa'])
    print('All sorifa ',len(allSorifa))
    
    bySorifa = {}
    compteur = 0
    tranche =199
    bornesup = tranche
    borneinf = 0
    while bornesup < len(allSorifa):
        ## Je cherche les id SF des code sorifa dont j'ai besoin
        """
        if bornesup>len(allSorifa):
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Lead where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:]])+')'
        else:
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Lead where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:bornesup]])+')'
        """
        if bornesup>len(allSorifa):
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:]])+')'
        else:
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:bornesup]])+')'
        
        csrSorifa = sf.query_all(qryFindFromSorifa)['records']
        compteur += 1
        borneinf =compteur*tranche
        bornesup = (compteur+1)*tranche
        ## print(len(csrSorifa))
        if bornesup >= len(allSorifa):
            bornesup = len(allSorifa)
        for r in csrSorifa:
            
            bySorifa[r['Code_Client_SOFIRA__c']]=(r['Id'],r['Name'])
            # pour la mise a jour
            ## bySorifa[r['Code_Client_SOFIRA__c']]=r['Id']
        ## print('inf',borneinf)
        # print('sup',bornesup)
    for k in  bySorifa.keys():
        print("%s;%s;%s"%(k,bySorifa[k][1],bySorifa[k][0]))
    print('sorifa trouvés', len(bySorifa))
    
    
    readyToUpdate =[]
    ## ya plus qu'a preparer un tableau de dict pour les update
    for k in unknownCompteByFacture.keys():
        
        for idLC in unknownCompteByFacture[k] :
            if k in byFacture.keys() and byFacture[k] in bySorifa.keys():
                readyToUpdate.append({'Id':idLC,'Compte__c':bySorifa[byFacture[k]][0] })
    
    print(len(readyToUpdate))
    print(readyToUpdate[-5:])
    compteur = 0
    tranche =100
    bornesup = tranche
    borneinf = 0
    
    
    
    ## r = sf.bulk.Commande__c.update(readyToUpdate)
    # print(r)
def findLeads():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    qry  ='SELECT id,Bon_de_livraison__c,Code_Client_EURODEP__c,Code_EAN_EURODEP__c,Compte__c,C_A_Brut__c,C_A_Net__c,Date_de_commande__c,Facture__c,Ligne__c,Prix_Brut__c,Prix_Net__c,Produit__c,Quantite__c,Reference_Client__c FROM Commande__c where compte__c = null and Code_Client_EURODEP__c = null  order by Date_de_commande__c desc'
    result = sf.query_all(qry)['records']
def ventesInternet():
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    allSorifa = []
    byFacture ={}
    
    with open('./Internet2017.csv','r') as f: # Internet2017.csv venteshisto.csv
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            # print(l['date mouvement'])
            dateclef='%s%s%s' %(l['date mouvement'][-4:],l['date mouvement'][3:5],l['date mouvement'][:2])
            ## print(dateclef)
            ## print(l['numero document']+dateclef)
            
            
            if (l['numero document']+dateclef) not in byFacture.keys():
                byFacture[l['numero document']+dateclef] = l['Code client sorifa']
            
            if l['Code client sorifa'] not in allSorifa:
                allSorifa.append(l['Code client sorifa'])
    print('All sorifa ',len(allSorifa))
    
    bySorifa = {}
    compteur = 0
    tranche =199
    bornesup = tranche
    borneinf = 0
    while bornesup < len(allSorifa):
        ## Je cherche les id SF des code sorifa dont j'ai besoin
        if bornesup>len(allSorifa):
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:]])+')'
        else:
            qryFindFromSorifa = 'select id,Code_Client_SOFIRA__c,Name from Account where Code_Client_SOFIRA__c in ('+','.join(["\'%s\'" % c for c in allSorifa[borneinf:bornesup]])+')'
        print(qryFindFromSorifa)
        csrSorifa = sf.query_all(qryFindFromSorifa)['records']
        compteur += 1
        borneinf =compteur*tranche
        bornesup = (compteur+1)*tranche
        ## print(len(csrSorifa))
        if bornesup >= len(allSorifa):
            bornesup = len(allSorifa)
        for r in csrSorifa:
            
            bySorifa[r['Code_Client_SOFIRA__c']]=(r['Id'],r['Name'])
            # pour la mise a jour
            ## bySorifa[r['Code_Client_SOFIRA__c']]=r['Id']
        ## print('inf',borneinf)
        # print('sup',bornesup)
    for k in  bySorifa.keys():
        print("%s;%s;%s"%(k,bySorifa[k][1],bySorifa[k][0]))
    print('sorifa trouvés', len(bySorifa))
    
    
    """readyToUpdate =[]
    ## ya plus qu'a preparer un tableau de dict pour les update
    for k in unknownCompteByFacture.keys():
        
        for idLC in unknownCompteByFacture[k] :
            if k in byFacture.keys() and byFacture[k] in bySorifa.keys():
                readyToUpdate.append({'Id':idLC,'Compte__c':bySorifa[byFacture[k]][0] })
    
    print(len(readyToUpdate))
    print(readyToUpdate[-5:])
    compteur = 0
    tranche =100
    bornesup = tranche
    borneinf = 0
    
    """
    
    ## r = sf.bulk.Commande__c.update(readyToUpdate)
            
if __name__ == '__main__':
    ## process()
    ventesInternet()