import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from ural.utils import  safe_urlsplit
from ural import normalize_url, is_url, ensure_protocol, urls_from_html, urls_from_text
from urllib.parse import urljoin, urlsplit
from tqdm import tqdm
import os 
import sys
import pathlib



class Crawler:

    def __init__(self, url, writing_dir_html, writing_dir_urls, n, actif = True):
        self.url = url
        self.writing_dir_html = writing_dir_html
        self.writing_dir_urls = writing_dir_urls
        self.reading_dir_url =""
        self.current_depth = 0
        self.max_depth = n
        self.actif = actif
    
    def get_content(self):
        """ return the html of the passed url and a list of all the url in it"""
        #self.profondeur -= 1
        req =""
        try:
            req = requests.get(self.url)
            #updating the url
        except:
            return("erreur de requetes")
        # localement par rapport au fichier csv ou l'on se trovue ? 
        time.sleep(0.20)
        html = BeautifulSoup(req.content, "lxml").prettify()
        ### ---get url
        urls_html = urls_from_text(html) # rappel : generator (yield, lazy iterator)
        urls_in = set()
        for url in urls_html:
            url = urlsplit(url).geturl()
            if is_url(url):
                if url not in urls_in:
                    urls_in.add(url)
        return(html,urls_in)
        
    
    #fonction pour récupérer le nombre de fichier urls dans une couche
    def file_number(self):
        #libraire os.path pour pas que ça pete avec un autre os
        os.chdir(self.reading_dir_url)
        count = 0
        for path in pathlib.Path(self.reading_dir_url.iterdir():
            if path.is_file():
                    count += 1
        return count
    

    def state_update_andwrite(self):
        if self.current_depth == self.max_depth + 1:
            self.actif = False
            return False
        
        #initialisation
        if self.current_depth == 0:
            couche = set()
            couche = self.get_content() #on recupere la couche 0 en fait
            self.current_depth += 1
            with open("{}/0.html".format(self.writing_dir_html),'w') as html_file:
                # ecriture du fichier html0
                html_file.write(couche[0])
                dossier = self.writing_dir_html.split("/")
                chemin = dossier.pop()
                self.writing_dir_html = "/".join(dossier)+ "/" + chemin[:len(chemin)-1] + str(self.current_depth)
            with open("{}/0.csv".format(self.writing_dir_urls),"w") as next_url_file:
                # ecriture urls contenus dans le fichier html0
                writer = csv.DictWriter(next_url_file, fieldnames=["FROM_HTML","URL"])
                writer.writeheader()
                x = 0
                for url in couche[1]:
                    writer.writerow({"FROM_HTML":"{}.html".format(x),"URL":url})
                    x += 1
                # le dossier de lecture devient celui de la couche qui vient d'etre traitée
                self.reading_dir_url = self.writing_dir_urls
                # on change le dossier d'ecriture
                dossier2 = self.writing_dir_urls.split("/")
                chemin2 = dossier2.pop()
                self.writing_dir_urls = "/".join(dossier2) + "/" + chemin2[:len(chemin2)-1] + str(self.current_depth)
                
            self.actif = True
            
            return True

        #hérédité
       
        nombre_fichiers_urlcsv = self.file_number()
        for x in range(nombre_fichiers_urlcsv):
            with open("{}/{}.csv".format(self.reading_dir_url,x)) as url_file : 
                file_content = csv.DictReader(url_file)
                compteur = 0
                for row in file_content:
                    if not is_url(row["URL"]) or type(row["URL"]) != str:
                        continue
                    self.url = row["URL"]
                    couche_suivante = self.get_content()
                    
                    with open("{}/{}.html".format(self.writing_dir_html,compteur),'w') as html_file:
                        html_file.write(couche_suivante[0])
                    with open("{}/{}.csv".format(self.writing_dir_urls,compteur),"w") as next_url_file:
                        writer = csv.DictWriter(next_url_file, fieldnames=["FROM_HTML","URL"])
                        writer.writeheader()
                        for url in couche_suivante[1]:
                            writer.writerow({"FROM_HTML":"{}.html".format(x),"URL":url})
                    compteur += 1
            #changement du dossier de lecture
            
        self.reading_dir_url= self.writing_dir_urls
        self.current_depth += 1 
        dossier = self.writing_dir_html.split("/")
        chemin = dossier.pop()
        self.writing_dir_html = "/".join(dossier) + "/" + chemin[:len(chemin)-1] + str(self.current_depth)

        dossier2 = self.writing_dir_urls.split("/")
        chemin2 = dossier2.pop()
        self.writing_dir_urls = "/".join(dossier2) + "/" + chemin2[:len(chemin2)-1] + str(self.current_depth)
        
        self.actif = True
        return True



crawl = Crawler("https://www.echojs.com/","/home/ptl7123/Bureau/test_scraping/code_html_cou0","/home/ptl7123/Bureau/test_scraping/url_cou0",2)

while crawl.actif:
    crawl.state_update_andwrite()





