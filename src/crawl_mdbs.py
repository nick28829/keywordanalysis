from bs4 import BeautifulSoup as BS
import pandas as pd
import re
import os

FILE = 'Abgeordneten.html'

if __name__=='__main__':
    os.system(f'curl https://www.bundestag.de/abgeordnete > {FILE}')

    names, firstNames, parties = [], [], []
    regex = re.compile(r"\(.*\)", re.IGNORECASE)

    with open(FILE) as file:
        soup = BS(file, 'html.parser')
        divs = soup.find_all('div', class_='bt-teaser-person-text')
        # print(divs)
        for div in divs:
            name = div.h3.text.strip('\n').strip(' ').split(', ')[0]
            name = regex.sub("", name)
            firstName = div.h3.text.strip('\n').strip(' ').split(', ')[1]
            names.append(name)
            firstNames.append(firstName.replace('Prof. ', '').replace('Dr. ', ''))
            parties.append(div.p.text.strip('\n').strip(' ').strip('\t'))

    mdbs = pd.DataFrame({'Name': names, 'First_Name': firstNames,'Party': parties})
    print(mdbs.head())
    mdbs.to_csv('MdBs.csv', index=False)