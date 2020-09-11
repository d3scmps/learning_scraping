import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from ural.utils import  safe_urlsplit
from ural import normalize_url, is_url, ensure_protocol,urls_from_text
from urllib.parse import urljoin
htm = 0 

def articles(url):
    """
    Given an echojs news page, this function collect and write specific informations
    about all articles that can be found on this page
    """
    global htm
    #### collecting the HTML
    time.sleep(0.3)
    page = requests.get(url)
    ### parsing the page with BeautifulSoup (getting the html)
    soup = BeautifulSoup(page.content, 'lxml')
    ### collecting articles tags
    articles = soup.select('article')
    articles_page = []
    ### extracting relevant information on those articles
    for article in articles:
        di = {"TITLE" : "", "LINK" : "", "AUTHOR":"", "NB_OF_COMMENTS" :"", "UP_NB" :" ", "DOWN_NB" :"","PATH_HTML": "","FILE_URLS_FROM_HTML":""}
        try :
            di["TITLE"] = article.find("h2").get_text().strip()
        except:
            di["TITLE"] = ""
        try :
            di["AUTHOR"] = article.find("username").get_text().strip()
        except:
            di["AUTHOR"] = ""
        try :
            di["LINK"]= article.find("a", {"rel": True}).get("href")
        except:
            di["LINK"]= ''
        try : 
            di["UP_NB"] = article.find("span",{"class": "upvotes"}).get_text().strip()
        except:
            di["UP_NB"] = 0
        try:
            di["DOWN_NB"] = article.find("span",{"class": "downvotes"}).get_text().strip()
        except:
            di["DOWN_NB"]=0
        try:
            di["NB_OF_COMMENTS"]= article.find('a', text = re.compile('comment$')).get_text()[0].strip()
        except:
            di["NB_OF_COMMENTS"] = 0
        articles_page.append(di)
        
        di["PATH_HTML"] = str(htm) + ".html"
        di["FILE_URLS_FROM_HTML"] = str(htm) +".txt"
        htm +=1

    return articles_page
  
def urls_generator(number):
    """ This function is used to generate a specific number of urls of echojs news page""" 
    urls =[]
    for i in range(number):
        path = "/latest/"+str(30*i)
        url = urljoin('https://www.echojs.com',path)
        urls.append(url)
    return urls


tx = 0 
### Scraping and writing information on articles that can be found on echojs news page into a csv file 
with open("/home/ptl7123/Bureau/scraping_exo/test.csv","w") as f2:
    writer = csv.DictWriter(f2, fieldnames=['TITLE', 'AUTHOR', 'LINK', 'UP_NB','DOWN_NB',"NB_OF_COMMENTS","PATH_HTML","FILE_URLS_FROM_HTML"])
    writer.writeheader()
    urls = urls_generator(10)
    for url in urls:
        articles_page = articles(url)
        for article in tqdm(articles_page):
            writer.writerow(article)
            #scraping html content that can be found following the link of the article
            if is_url(article['LINK']):
                f2 = open('/home/ptl7123/Bureau/scraping_exo/code_html/'+ article["PATH_HTML"], "w") # changer le nom (hash : ND5, hashlib) (ou fonction bijective)
                time.sleep(0.3)
                try:
                    page = requests.get(ensure_protocol(article['LINK']))
                    html = BeautifulSoup(page.content, 'lxml')
                    f2.write(html.prettify())
                    #scraping URLS that can be found within the html content found following the link of the article
                    f3 = open('/home/ptl7123/Bureau/scraping_exo/url_html/'+str(tx)+".txt","w")
                    tx +=1
                    try :
                        urls = urls_from_text(html.get_text())
                        for url in urls:
                            f3.write(url + "\n")
                    except:
                        f3.write("pas d'urls dans ce contenu html")
                    
                except:
                    f2.write(article['LINK'] + "\n" + "site impossible à request")
                
        