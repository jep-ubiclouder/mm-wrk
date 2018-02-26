import sys

def prepareMapChamps():
    import csv
    resultat = {"drup2SF":{},"internSF":{}}
    with open('./mapping.club.company.csv','r') as mapCSV:
        lecteur = csv.DictReader(mapCSV,delimiter=';')
        for r in lecteur:
            if r['To be imported?'] != 'VRAI':
                continue
            if len(r['Drupal Field'])>0  and r['Drupal Field'] != 'All' :
                resultat['drup2SF'][r['Drupal Field']] =r
                ##cif r['Salesforce Object'] not in resultat['drup2SF'].keys():
                ##c    resultat['drup2SF'][r['Salesforce Object']] ={}
            elif r['Drupal Field'] == "All":
                resultat['drup2SF'][r['Drupal Field']] ='All'
            else:   # r['Drupal Field'] est vide
                if r['Salesforce Object'] not in resultat['internSF'].keys():
                ##c    resultat['drup2SF'][r['Salesforce Object']] ={}
                    resultat["internSF"][r['Salesforce Object']]={}
                resultat["internSF"][r['Salesforce Object']][r['Salesforce Field']]=r['Default Value']
    return resultat


def processData(mdc):
    """
    ecrits dans salesforce a partir du fichier csv et de la map des champs
    
    update account
    insert Data_Origin_Account__c
    insert Data_Integration_Account__c
    """
    import pprint
    import csv
    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(mdc)
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
    sf = Salesforce(username='hp@maisonmoderne.lu.1assembdev', password='Ubi$2018', security_token='KhrfeUNWQz8Z60PDIKG8G8vO', sandbox=True)
    
    qryAccId =  "select Cle_Client_STOCKX__c,Id from account"
    byCSTX = {}
    records = sf.query_all(qryAccId)['records']
    for r in records:
        byCSTX[r['Cle_Client_STOCKX__c']]=r['Id']
    
    with open('./export_club_soc__main.csv','r') as dataDrup:
        readData = csv.DictReader(dataDrup,delimiter=';')
        cpte =0
        byLigne={}
        for ligne in readData:
            
            recordSF ={}
            byLigne[ligne['field_club_soc_id_stockx']]={'Account':{},'Data_Integration_Account__c':mdc['internSF']['Data_Integration_Account__c'],'Data_Origin_Account__c':mdc['internSF']['Data_Origin_Account__c']}
            #pp.pprint(byLigne[ligne['field_club_soc_id_stockx']])
            ##  pp.pprint(ligne)
            for clef in ligne.keys():
                if clef in mdc['drup2SF'].keys():
                ##print('clef',clef)
                ##    print('mdc[clef]',mdc['drup2SF'][clef])
                ##     print('mdc[clef][sf]',mdc['drup2SF'][clef]['Salesforce Field']) """
                    objet = mdc['drup2SF'][clef]['Salesforce Object']
                    champ =mdc['drup2SF'][clef]['Salesforce Field']
                    byLigne[ligne['field_club_soc_id_stockx']][objet][champ]=ligne[clef]
                byLigne[ligne['field_club_soc_id_stockx']]['Data_Integration_Account__c']['Account__c'] = byCSTX[ligne['field_club_soc_id_stockx']]
                byLigne[ligne['field_club_soc_id_stockx']]['Data_Origin_Account__c']['Account__c'] = byCSTX[ligne['field_club_soc_id_stockx']]     
                byLigne[ligne['field_club_soc_id_stockx']]['Data_Origin_Account__c']['Additional_Reference__c'] = ligne    
                    
                    
            pp.pprint(byLigne[ligne['field_club_soc_id_stockx']])
            cpte += 1
            if cpte > 10 :
                import sys
                sys.exit()
        
    pass
if __name__=='__main__':
    mapDC = prepareMapChamps()
    processData(mapDC)