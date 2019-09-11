import os
from bs4 import BeautifulSoup
import requests

p_count = 1
for i in range(1,7):
    url = 'https://www.nature.com/natmachintell/volumes/1/issues/' + str(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    articles = soup.find(id = 'Research-content')
    articles = articles.find_all(class_ = 'cleared')
    for article in articles:
        title = article.select('h3 a')[0].text
        title = title.replace('\n','')
        title = title.lstrip()
        t_url = 'http://www.nature.com' + article.select('h3 a')[0]['href']
        abstract = article.select('div p')[1].text

        print(str(p_count) + '. ' + title)
        print(t_url)
        print(abstract)
        print()
        p_count += 1
    x = 1