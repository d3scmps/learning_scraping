import csv
import time
import requests
import re
from bs4 import BeautifulSoup
from ural.utils import  safe_urlsplit 


def articles(URL,fichier):
    """
    Given an echojs news page, this function collect and write specific informations
    about all articles that can be found on this page
    """
    #### collecting the HTML
    page = requests.get(URL)

    ### parsing the page with BeautifulSoup (getting the html)

    soup = BeautifulSoup(page.content, 'html.parser')

    #selecting the tag object 
    html = list(soup.children)[1]

    ### html tags

    tags = list(html.children) #head is [1], body is [3]
    body = tags[3]
    body2 = list(body)


    first_article = body.find('article')
    articles = [first_article] #l
    next_articles = body.article.next_siblings #j

    #### --- getting rid of selection noises, only keeping Tag elements
    for article in next_articles:
        # type(l[0]) == bs4.Tag
        if not isinstance(article,type(articles[0])):
            continue
        else:
            articles.append(article)

    articles_page =[]

    for article in articles:
        di = {"TITLE" : "", "LINK" : "", "AUTHOR":"", "nb_of_comments" :"", "up_nb" :" ", "down_nb" :""}
        try :
            di["TITLE"] = article.find("h2").get_text()
        except:
            di["TITLE"] = "none"
        try :
            di["AUTHOR"] = article.find("username").get_text()
        except:
            di["AUTHOR"] = "none"
        try :
            di["LINK"]= article.find("a", {"rel": True})['href']
        except:
            di["LINK"]= 'none'
        try : 
            di["up_nb"] = article.find("span",{"class": "upvotes"}).get_text()
        except:
            di["up_nb"] = 0
        try:
            di["down_nb"] = article.find("span",{"class": "downvotes"}).get_text()
        except:
            di["down_nb"]=0
        commentary = article.find('a', text = re.compile('comment$'))
        if commentary:
            di["nb_of_comments"]= commentary.get_text()[0]
        else:
            di["nb_of_comments"] = 0
        articles_page.append(di)

    articles_page.pop() # removing last line (always return none)

    with open(fichier,"a") as f2:
        writer = csv.DictWriter(f2, fieldnames=['TITLE', 'AUTHOR', 'LINK', 'up_nb','down_nb',"nb_of_comments"])
        for article in articles_page:
            writer.writerow(article)


def get_all_urls(start_url,urls = [], stop = 300, c = 0):
    """ 
    Given a specific "latest news echo js" URl, this function crawls inside all 
    "latest news echo js page" (to a given limit)"""
    page = requests.get(start_url)
    splitted_url = safe_urlsplit(start_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    more = soup.find("a", {"class": "more"})
    if more and c <= stop:
        c+=30
        path = more['href'] 
        url = splitted_url.scheme + "://"+ splitted_url.netloc + path + splitted_url.query + splitted_url.fragment
        urls.append(url)
        return get_all_urls(url,urls = urls,c=c)
    else:
        return urls

start_url = "https://www.echojs.com/latest/30"
urls = get_all_urls(start_url)

with open(fichier,"w") as f2:
    writer = csv.DictWriter(f2, fieldnames=['TITLE', 'AUTHOR', 'LINK', 'up_nb','down_nb',"nb_of_comments"])
    writer.writeheader()

for url in urls:
    articles(url,"test.csv")