import praw
import os as os
import re as re
import pandas as pd
from pandas import Series,DataFrame
import csv
from bs4 import BeautifulSoup
import html5lib
import urllib
import requests
import string


terms_list=[]
terms_dict={}

no_info ="Sorry I wasn't able to find this in my database, but I will update it as soon as possible! This could be due to a spelling or syntax error. Please make sure to use the proper command styles: ssb_bot define [smash_term], ssb_bot charactername [gound_moves, aerials, specials, properties, or all_moves], or ssb_bot info."
signature = "This bot quickly provides information on Super Smash Bros lingo, characters, and events. Please message me with any suggestions or problems. To define Smash terms, type **ssb_bot define [smash_term]**. For frame data, type **ssb_bot [charactername]** followed by one of the following: **ground_moves/ aerials/ specials/ or properties**. For more information type **ssb_bot info**"

character_list=['Bayonetta','Bowser','Bowser Jr','Captain Falcon','Charizard','Cloud','Corrin',
                'Dark Pit','Diddy Kong','Donkey Kong','Dr. Mario','Duck Hunt','Falco','Fox','Ganondorf',
                'Greninja','Ike','Jigglypuff','King Dedede','Kirby','Link','Little Mac','Lucario','Lucas',
                'Lucina','Luigi','Mario','Marth','Mega Man','Meta Knight','Mew Two','Mii Swordfighter',
                'Mii Brawler','Mii Gunner','Game and Watch','Ness','Olimar','Pacman','Palutena','Peach',
                'Pikachu','Pit','R.O.B','Robin','Rosalina and Luma','Roy','Ryu','Samus','Sheik','Shulk',
                'Sonic','Toon Link','Villager','Wario','Wii Fit Trainer','Yoshi','Zelda','Zero Suit Samus']

#ssbwiki/terms data
def soup_maker(terms_dict, terms_list, ssb_soup):
    next_url= ssb_soup.find('div',{'class':'mw-allpages-nav'})
    next_url = next_url.find('a').find_next().get('href')
    if not next_url: return
    next_url = requests.get('https://www.ssbwiki.com' + next_url)
    ssb_soup = BeautifulSoup(next_url.text,'lxml')
    write_page(terms_dict, terms_list,ssb_soup)
    return ssb_soup

def write_page(terms_dict, terms_list, ssb_soup):
    wiki_page = ssb_soup.find('ul',{'class':'mw-allpages-chunk'})
    for link in wiki_page.find_all('li'):
        index = link.get_text()
        if not index.lower().endswith('(disambiguation)'): 
            cleaned_index = index.split(maxsplit=15)
            for word in range(0,len(cleaned_index)):
                cleaned_index[word]=re.sub('[\W\s]','',cleaned_index[word])
                cleaned_index[word]=re.sub('(ing|ly|ed|ious|ies|ive|es|s|ment)?$','',cleaned_index[word])
            cleaned_index=''.join(cleaned_index)
            cleaned_index=cleaned_index.lower() 

            index_link=link.find('a').get('href')
            index_link='https://www.ssbwiki.com' + index_link

            terms_list.append([cleaned_index,index_link])
            terms_dict[cleaned_index]=index_link




ssb_url = requests.get('https://www.ssbwiki.com/index.php?title=Special:AllPages&from=%21+Block')
ssb_soup= BeautifulSoup(ssb_url.text,'lxml')
write_page(terms_dict, terms_list, ssb_soup)

next_html = ssb_soup.find('div', {'class':"mw-allpages-nav"})
next_url = next_html.find('a').get('href')
next_url = requests.get('https://www.ssbwiki.com' + next_url)
ssb_soup = BeautifulSoup(next_url.text,'lxml')
write_page(terms_dict,terms_list,ssb_soup)

while ssb_soup:
    ssb_soup = soup_maker(terms_dict, terms_list, ssb_soup)
    if ssb_soup is None:
        break
    write_page(terms_dict,terms_list, ssb_soup)  
    
with open('terms.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for each in terms_list:
        writer.writerow(each)
    f.close()

#KuroganeHammer/Character stuff
smash_url = requests.get('http://kuroganehammer.com/Smash4')
smash_soup = BeautifulSoup(smash_url.text,'lxml')

character_links=[]
for link in smash_soup.find_all('a'):
    character_links.append(link.get('href'))


character_links=character_links[11:] 
character_links.remove('/Smash4/Mii')
character_links.insert(31, '/Smash4/Mii%20Gunner')
character_links.insert(31, '/Smash4/Mii%20Brawler')
character_links.insert(31, '/Smash4/Mii%20Swordfighter')


counter=0
for each in character_links:
    url = 'http://kuroganehammer.com%s'%(each)
    dframe_list = pd.read_html(url,encoding='utf-8')
    dframe_all = pd.concat(dframe_list, axis=1)
    character = character_list[counter]+'.csv'
    counter+=1
    if not os.path.exists(character): 
        with open(character, 'a',encoding='utf-8') as f:
            dframe_all.to_csv(f,encoding='utf-8',index=False)
    else:
        with open(character, 'w',encoding='utf-8') as f:
            dframe_all.to_csv(f,encoding='utf-8',index=False)


print("Done")
