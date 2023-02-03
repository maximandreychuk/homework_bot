import requests
from bs4 import BeautifulSoup 
import pandas 

IMAGE_COUNTER = 0
URL_TEMPLATE = 'https://www.vovatit.com/artworks'
response = requests.get(URL_TEMPLATE).text

soup = BeautifulSoup(response, 'lxml')
block = soup.find('div', class_ = 'w-dyn-list')
block_image = block.find_all('div', class_ = 'collection-item w-dyn-item w-col w-col-4')

for image in block_image:
    link = image.find('img').get('src')
    link_photo = requests.get(link).content

    with open(f'images/{IMAGE_COUNTER}.jpg', 'wb') as file:
        file.write(link_photo)

    IMAGE_COUNTER += 1
    print(f'{IMAGE_COUNTER} скачано')

