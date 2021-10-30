import requests, re, json, bs4
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd

def get_html_content(url:str) -> str:
    html_response = requests.get(url)
    soup = BeautifulSoup(html_response.content, 'html.parser')
    return soup

def get_all_articles_links_n_ids(soup):
    urls_list = []
    links = soup.find_all("a")
    
    for link in links:
        art_url = link.get('href') # get the url

        # Here we take only the articles in to our url_list
        if "item" in art_url:
            urls_list.append(art_url)

    urls_list = list(set([url[:url.find('?')] if '?' in url else url for url in urls_list])) # make sure the url is clean
    articles_id_list = [url[-7:] for url in urls_list] # take the url_id

    return urls_list, articles_id_list

def get_article_tags(soup):
    tag_links = soup.find_all("a", href=re.compile("tags.walla.co.il"))
    tags = [ele.text for ele in tag_links]
    return tags

# Creating the function that takes the comments content, likes, and dislikes
def get_article_talkbacks(url, article_id):
    url_page, url_type = 1, 1
    url_final = url.format(article_id)
    comments = []
    while True:
        # give the api the paramaeters for finding the comments
        html_response = requests.get(url_final, params={'page': url_page, 'type': url_type})
        if html_response.status_code != 200:
            break
        
        # moving to the next comments page
        url_page += 1

        content = json.loads(html_response.content, encoding='utf-8')
        data = content['data']
        # check if we are at the last page of the comments or the article doesn't have any comments
        if not data:
            break
        
        # Get the content/ likes/ dislikes from the comment
        data = data['list']
        for entry in data:
            comment = [article_id, entry['content'], entry['positive'], entry['negative']]
            comments.append(comment)

    return comments

def create_talkbacks_df(articles_id_list):
    articles_without_talkbacks = []
    for article_id in articles_id_list:
        comments = get_article_talkbacks('https://dal.walla.co.il/talkback/list/{}', article_id)
        if not comments:
            articles_without_talkbacks.append(article_id)
            continue
    talkbacks = pd.DataFrame(comments,columns=['article_id','comment_text','likes','dislikes'])
    return talkbacks

def get_article_headline(soup):
    header_tag = soup.find('h1').get_text()
    return header_tag 

def get_article_publish_dt(soup):
    time = soup.find('time')
    if time:
        #print(time)
        dt = time["datetime"]
        #print(dt)
        return dt

    time = soup.find('span', class_= 'pubdate')
    if isinstance(time, bs4.element.Tag):
        return time.text

    return 'null'

def create_articles_table(article_ids,publish_dates,headlines,tags):
    articles = pd.DataFrame({'article_id':article_ids,'publish_date':publish_dates,'headline':headlines,'tags':tags})
    return articles

def fix_hebrew(tag):
    return tag[::-1]

if __name__ == '__main__':
    start_time = time.perf_counter ()

    WALLA_URL = "https://www.walla.co.il/"
    soup = get_html_content(WALLA_URL)
    urls_list, articles_id_list = get_all_articles_links_n_ids(soup)

    tags, headlines, publish_dates = [], [], []
    for url in urls_list:
        article_soup = get_html_content(url)
        # Get all the tags, headlines and publishdates from all the articles in the main walla page
        tags.append([fix_hebrew(tag) for tag in get_article_tags(article_soup)])
        headlines.append(get_article_headline(article_soup))
        publish_dates.append(get_article_publish_dt(article_soup))

    #create the talkbacks df
    talkbacks_df = create_talkbacks_df(articles_id_list)
    #talkbacks_df.to_csv('Walla_talkbacks_df.csv', encoding='utf-8')

    articles_df = create_articles_table(articles_id_list,publish_dates,headlines,tags)
    #articles_df.to_csv('Walla_articles_df.csv', encoding='utf-8')
    
    final_df = articles_df.merge(talkbacks_df, on='article_id', how='left')
    #final_df.to_csv('Walla_final_df.csv', encoding='utf-8')

    end_time = time.perf_counter ()
    print(end_time - start_time, "seconds")
    # TESTS

    # check single article output
    #print(get_article_talkbacks('https://dal.walla.co.il/talkback/list/{}', 3379189))
