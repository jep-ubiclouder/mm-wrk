import sys

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
    return creds



def process():

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
    isTest = False
    creds = getCredentials(isTest)
    
    sf = Salesforce(username=creds['user'], password=creds['passwd'], security_token=creds['security_token'], sandbox=isTest)
    
    """queryAllAccount = 'select id, Name, ParentId,Descriptif__c from Account'
    
    cursor = sf.query_all(queryAllAccount)
    records =  cursor['records']
    i = 0
    for rec in records:
        ## print(rec)
        
        if rec['Descriptif__c'] is not None and len(rec['Descriptif__c'])>0:
            print(rec['Descriptif__c'],rec['Name'])
    print('Nbre de records ds account')
    print(len(records))
    """
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    fieldsToQuery =[]
    fieldsToExclude = []
    for t in  sf.Account.describe()['fields']:
        if t['compoundFieldName'] is not None and t['compoundFieldName'] not in fieldsToExclude:
            fieldsToExclude.append(t['compoundFieldName'])
    for t in  sf.Account.describe()['fields']:
        if t['name'] not in fieldsToExclude and t['calculated'] == False:
            fieldsToQuery.append(t['name'])

    queryAllAccount = 'select '+','.join(fieldsToQuery) +' from Account'
    print(queryAllAccount)
    cursor = sf.query_all(queryAllAccount)
    records =  cursor['records']
    i = 0
    
        
    print('Nbre de records ds account')
    print(len(records))
    import csv
    with open('./Account.csv','w') as f:
        w= csv.writer(f,delimiter=';')
        r = records[0]
        w.writerow(r.keys())
        for rec in records:
            w.writerow(rec.values())
            
    for rec in records:
            print(rec)            
    
if __name__ == '__main__':
    process()