'''
Created on 8 juin 2017

@author: jean-eric preis
'''
from simple_salesforce import Salesforce
sf = Salesforce(username='jep@ubitask2.com', password='Ubi$2017', security_token='bnWf5zUKZg8hPjPP5Qein2HW')

compte = sf.query("Select  id,name from Account  where AccountNumber = 'CD656092'")
print(compte['records'])


from simple_salesforce import SFType

reponse = sf.ubTAsks__Tasks_per_Status__c.describe()
print(reponse)
"""import os.path
import csv
with open('./bucket-mm-daily/lo-2017-test.csv', 'r') as csvfile:
        reader=  csv.reader(csvfile,delimiter=';')
        for row in reader:
                print row
"""
if __name__ == '__main__':
    pass
