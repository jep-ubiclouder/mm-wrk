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
    
    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(mdc)
    
    
    pass
if __name__=='__main__':
    mapDC = prepareMapChamps()
    processData(mapDC)