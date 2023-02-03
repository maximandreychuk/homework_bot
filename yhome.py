import requests
from bs4 import BeautifulSoup 
import pandas 

URL_TEMPLATE = "https://www.pressfoto.ru/galleries/trends-2017"
r = requests.get(URL_TEMPLATE)
try:
    f = open('example_1.txt', 'w')
    f.write(r.text)  
    f.close()  
except Exception as error:
    print(error)