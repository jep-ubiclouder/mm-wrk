from  xml.dom.minidom import parse,parseString
import sys



if __name__ == "__main__":
    pass
    dom1 = parse('./schema.xml')
    lines = dom1.getElementsByTagName("mapperTableEntries")
    for l in lines:
        print(l.getAttribute('name'),'=>',l.getAttribute('expression'))
    cpt = 0   
    with open('./finalImport.csv','r') as f: # Internet2017.csv venteshisto.csv
        reader = csv.DictReader(f, delimiter=';')
        for l in reader:
            cpt +=1 
    print(cpt)