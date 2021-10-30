from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
import json

def get_html_content(url:str) -> str:
    html_response = requests.get(url)
    soup = BeautifulSoup(html_response.content, 'html.parser')
    return soup

def get_article_links_n_ids(soup):
    urls_list = []
    links = soup.find_all("a")
    
    for link in links:
        art_url = link.get('href') # get the url

        # Here we take only the articles in to our url_list
        if "item" in art_url:
            urls_list.append(art_url)

    urls_list = list(set([url[:url.find('?')] if '?' in url else url for url in urls_list])) # make sure the url is clean
    articles_id = [url[-7:] for url in urls_list] # take the url_id

    return urls_list, articles_id


def get_article_tags(soup):
    tag_links = soup.find_all("a", href=re.compile("tags.walla.co.il"))
    tags = [ele.text for ele in tag_links]
    return tags
    

if __name__ == '__main__':
    WALLA_URL = "https://www.walla.co.il/"
    soup = get_html_content(WALLA_URL)
    
    urls_list, articles_id = get_article_links_n_ids(soup)
    print(len(urls_list), urls_list[0])
    print("-------------------------------")
    print(len(articles_id), articles_id[0])
    print("-------------------------------")

    # Creat a list that would save the times of the crawler entering to articles
    # crawler_dt = []
    first_url_content = get_html_content(urls_list[0])
    print(get_article_tags(first_url_content))
