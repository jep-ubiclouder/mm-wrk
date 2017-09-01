from cryptography.fernet import Fernet
clef =b'y1RrSzZel5RRjMjCZwwLVnVppKzqHQT0v-Mm96WNdS4='

import json

credentials ={'user':'jep@assembdev.com', 'passwd':'ubi$2017', 'security_token':'aMddugz7oc45l1uhqWAE308Z'}

strCreds =  json.dumps(credentials)
print(strCreds)
cipher =  Fernet(clef)
print(cipher.encrypt(bytes(strCreds,'UTF-8'))