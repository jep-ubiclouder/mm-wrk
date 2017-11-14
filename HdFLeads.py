from  xml.dom.minidom import parse,parseString
import sys
import csv
from simple_salesforce import (Salesforce, SalesforceAPI, SFType, SalesforceError, SalesforceMoreThanOneRecord, SalesforceExpiredSession, SalesforceRefusedRequest,
    SalesforceResourceNotFound, SalesforceGeneralError, SalesforceMalformedRequest)

if __name__ == "__main__":
    pass
    dom1 = parse('./schema.xml')
    lines = dom1.getElementsByTagName("mapperTableEntries")
    mapChamps = {}
    for l in lines:
        if len(l.getAttribute('expression'))> 3 :
            # print('source', l.getAttribute('expression'))
            source = l.getAttribute('expression').split('.')[1]
            dest = l.getAttribute('name')
            mapChamps[source] = dest 
            print(source ,'=>', dest)
    cpt = 0 
    allGroupement = []
      
                
    qryGroupement =  'select id,Name from Groupement__c'            
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    groups =  sf.query_all(qryGroupement)['records']
    groupsByName ={}
    for g in groups:
        groupsByName[g['Name']] = g['Id']

    inserts = []
    with open('./finalImport.csv','r') as f: # Internet2017.csv venteshisto.csv
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            cpt +=1
            for elem in l:
                if len(l[elem])>0:
                    print(elem,l[elem])
            # 'Categorie_de_client__c'='a020Y000002lgVTQAY''
            #'Tarif'= 'a030Y000003HzI2QAK'
            # 'Reglement' = 'a050Y000000kCUPQA2'
            if cpt > 3:
                sys.exit()
    print(cpt)