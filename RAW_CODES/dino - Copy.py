import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

# URL to scrape
url = 'https://en.wikipedia.org/wiki/List_of_dinosaur_genera'

# Get the HTML content of the page
html = requests.get(url)
# print(html.text)
# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html.text, features='html.parser')
# print(soup)
# # Find all anchor tags with href attribute
urls = soup.find_all('a', href=True)
# print(urls)
# Create list of (URL, text) tuples
links_and_names = [(url['href'], url.text) for url in urls]
# Print the result
#print(links_and_names)

dino_data_clean = [
    links_and_names[link]
    for link in range(len(links_and_names))
    if links_and_names[link][0].startswith("/wiki/")
]
dino_data_clean = dino_data_clean[:2317]

# print(dino_data_clean)
#
dino_df = pd.DataFrame(dino_data_clean, columns=['url', 'dinosaur'])
#print(dino_df.head(20))
#
dino_df['dinosaur'] = dino_df['dinosaur'].replace('', np.nan)
dino_df = dino_df.dropna(axis=0, subset=['dinosaur'])
dino_data_clean = dino_df.set_index('url')['dinosaur'].to_dict()
#print(dino_data_clean)

# Now we get the final real urls and names of dinosaurs as a tuple
dino_data=[('https://en.wikipedia.org' + url, dinosaur) for url, dinosaur in dino_data_clean.items()]
print(dino_data)
# Removes the first 33 items (likely irrelevant Wikipedia internal links or headers).
dino_data=dino_data[33::]
# print(dino_data)

#  valid list comprehension to extract URLs from a list of tuples like:
dino_urls = [element for pair in dino_data for element in pair if element.startswith('https://en.wikipedia.org')]
#print(dino_urls)

# create empty list
dino_info= []
# print(dino_info)

#
progress=0

# You're looping through the first 200 dinosaur URLs stored in dino_urls.
for url in range(200):
    html = requests.get(dino_urls[url])
    soup = BeautifulSoup(html.text, 'html.parser')
    paragraphs = soup.select('p')

    # Extracts and cleans the text from each <p> tag.
    clean_paragraphs = [paragraph.text.strip() for paragraph in paragraphs]

    # Keeps only the first 4 paragraphs. These usually contain the intro content.
    clean_paragraphs = clean_paragraphs[:4]
    # Joins those paragraphs into a single string and adds it to dino_info.
    dino_info.append(' '.join(clean_paragraphs))
    # print(dino_info)
    progress += 1


dino_df = pd.DataFrame(dino_data, columns = ['urls','dinosaur'])
# print(dino_df)

dino_details= pd.DataFrame(dino_df, columns=['Info'])

# print(dino_info)

dino_df = pd.concat([dino_df,dino_details], ignore_index = True, axis = 1)
# print(dino_df)

file_name = r'/home/ec2-user/demo/dino_data.xlsx'

dino_df.to_excel(file_name, index=False)
#
print('DataFrame is written to Excel File successfully!')
if 'Unnamed: 0' in dino_df.columns:
    dino_df.drop('Unnamed: 0', inplace=True, axis=1)

dino_df.columns = ['URLs', 'Dinosaur', 'Info']

dino_info = dino_df['Info'].to_dict()
print(dino_info)
dino_info = dino_info.values()

heights =[]
progress = 0

for element in dino_info:
    if re.findall('\d+\smeters', str(element)):
        height = re.findall('\d+\smeters', str(element))
        heights.append(height)
    else:
        heights.append(list('-'))
    progress += 1


heights_clean = []

for element in heights:
    for height in enumerate(element):
        if height[0] == 0:
            heights_clean.append(height[1])
weights = []
for element in dino_info:
    if re.findall(r'\d+stonnes|\d+skilograms', str(element)):
        weight = re.findall(r'\d+stonnes|\d+skilograms', str(element))
        weights.append(weight)
    else:
        weights.append(list(['-']))

weights_clean = []
for element in weights:
    for weight in enumerate(element):
        if weight[0] == 0:
            weights_clean.append(weight[1])

dino_df.drop('Info', inplace=True, axis=1)
heights_df = pd.DataFrame(heights_clean, columns=['Height'])
weights_df = pd.DataFrame(weights_clean, columns=['Weight'])
dino_df = pd.concat([dino_df, heights_df, weights_df], ignore_index=True, axis=1)

dino_df.columns = ['URL', 'Dinosaur', 'Height', 'Weight']
dino_df.to_excel(file_name)
print('DataFrame successfully exported to CSV file!')