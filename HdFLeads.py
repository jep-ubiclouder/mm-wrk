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
            source = l.getAttribute('expression').split('.')[1][:-1]
            dest = l.getAttribute('name')
            mapChamps[source] = dest 
            print(source ,'=>', dest)
    cpt = 0 
    allGroupement = []
      
                
    qryGroupement =  'select id,Name from Groupement__c'            
    sf = Salesforce(username='projets@homme-de-fer.com', password='ubiclouder$2017', security_token='mQ8aTUVjtfoghbJSsZFhQqzJk')
    
    tobeDel =[]
    qryDelete = 'SELECT Id from Lead WHERE CreatedDate >=2017-11-14T13:29:00Z'
    cpte = 0
    recordstodelete = sf.query_all(qryDelete)['records']
    for r in recordstodelete:
        tobeDel.append(r['Id'])
        cpte += 1
        for cpte > 950:
            sf.bulk.lead.delete(tobeDel)
            cpte= 0
            tobeDel=[]
    sf.bulk.lead.delete(tobeDel)
    groups =  sf.query_all(qryGroupement)['records']
    groupsByName ={}
    for g in groups:
        groupsByName[g['Name']] = g['Id']

    inserts = []
    with open('./finalImport.csv','r') as f: # Internet2017.csv venteshisto.csv
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            cpt +=1
            rec = {}
            for elem in l :
                if len(l[elem])>0 and elem in mapChamps.keys():
                    rec[mapChamps[elem]] = l[elem]
                    # print(elem,l[elem],mapChamps[elem])
            if len(rec)> 0:
                rec['Categorie_de_client__c']='a020Y000002lgVTQAY'
                rec['Tarif__c']= 'a030Y000003HzI2QAK'
                rec['Reglement__c'] = 'a050Y000000kCUPQA2'
                rec['Status'] = 'Nouveau'
                
                rec['Company'] =l['F_Raison_sociale']
                rec['LastName'] =l['F_Raison_sociale']
                rec['Type_TVA__c']='Soumis'
                if len(l['Groupement_1'])> 0:
                    if l['Groupement_1'] in groupsByName.keys():
                        print(group)
                inserts.append(rec)
            #'Tarif'= 'a030Y000003HzI2QAK'
            # 'Reglement' = 'a050Y000000kCUPQA2'
            if cpt > 350:
                print(rec)
                ## sys.exit()
                ## sf.bulk.Lead.insert(inserts)
                cpt = 0
                inserts =[]
                # sys.exit()
    print(cpt)
    # sf.bulk.Lead.insert(inserts)