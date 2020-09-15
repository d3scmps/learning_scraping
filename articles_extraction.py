import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from ural.utils import  safe_urlsplit
from ural import normalize_url, is_url, ensure_protocol, urls_from_html, urls_from_text
from urllib.parse import urljoin, urlsplit
from tqdm import tqdm
HTM = 0 
NB_LIENS = 0

def articles(url):
    """
    Given an echojs news page, this function collect and write specific informations
    about all articles that can be found on this page
    """
    global HTM
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
        
        di["PATH_HTML"] = str(HTM) + ".html"
        di["FILE_URLS_FROM_HTML"] = str(HTM) +".txt"
        HTM +=1

    return articles_page
  
def urls_generator(number):
    """ This function is used to generate a specific number of urls of echojs news page""" 
    for i in range(number):
        path = "/latest/"+str(30*i)
        url = urljoin('https://www.echojs.com',path)
        yield url


tx,td  = 0,0 
### Scraping and writing information on articles that can be found on echojs news page into a csv file 
with open("/home/ptl7123/Bureau/scraping_exo/test.csv","w") as article_file:
    writer = csv.DictWriter(article_file, fieldnames=['TITLE', 'AUTHOR', 'LINK', 'UP_NB','DOWN_NB',"NB_OF_COMMENTS","PATH_HTML","FILE_URLS_FROM_HTML"])
    writer.writeheader()
    urls = urls_generator(10)
    for url in urls:
        articles_page = articles(url)
        print("traitement de l'url :{}".format(url))
        for article in tqdm(articles_page):
            writer.writerow(article)
            #scraping html content that can be found following the link of the article
            url1 = urlsplit(article['LINK']).geturl()
            if is_url(url1):
                with open('/home/ptl7123/Bureau/scraping_exo/code_html_couche1/'+ article["PATH_HTML"], "w") as html_file1: 
                    time.sleep(0.3)
                    page = requests.get(ensure_protocol(url1))
                    html = BeautifulSoup(page.content, "html.parser")
                    html_file1.write(html.prettify())
                    url_in = set()
                    #scraping URLS that can be found within the html content found following the link of the article
                    with open('/home/ptl7123/Bureau/scraping_exo/url_html_couche1/{}.csv'.format(tx),"w") as url_html_file1:
                        writer2 = csv.DictWriter(url_html_file1, fieldnames=["FROM_HTML","URL","TO_HTML"])
                        writer2.writeheader()
                        tx += 1
                        urls = urls_from_text(html.prettify())
                        for url in urls:
                            if url not in url_in:
                                NB_LIENS +=1
                                url_in.add(url)
                                url = urlsplit(url)
                                td +=1
                                writer2.writerow({"FROM_HTML":article["PATH_HTML"],"URL":url.geturl(), "TO_HTML": str(td)+".html"})


print(NB_LIENS)   
        