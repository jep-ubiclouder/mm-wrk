from  xml.dom.minidom import parse,parseString
import sys



if __name__ == "__main__":
  pass
  dom1 = parse('./schema.xml')
  lines = dom1.getElementsByTagName("mapperTableEntries")
  for l in lines:
   print(l.getAttribute('name'))   
   print(l.getAttribute('expression'))