import praw
import csv
import pandas as pd
from pandas import Series,DataFrame
import re as re
import os as os
import requests
from bs4 import BeautifulSoup
import html5lib
import string
import time
from tabulate import tabulate

#constants
no_info ="Sorry I wasn't able to find this in my database, but I will update it as soon as possible!"
signature = "This bot quickly provides information on Super Smash Bros lingo, characters, and events. Please pm with suggestions or problems at /u/sidwasnthere. To define Smash terms, type **ssb_bot define [smash_term]**. For frame data, type **ssb_bot [charactername]** followed by one of the following: **ground_moves, aerials, specials, or properties**. For more information type **ssb_bot info**."

character_list=['Bayonetta','Bowser','Bowser Jr','Captain Falcon','Charizard','Cloud','Corrin',
                'Dark Pit','Diddy Kong','Donkey Kong','Dr. Mario','Duck Hunt','Falco','Fox','Ganondorf',
                'Greninja','Ike','Jigglypuff','King Dedede','Kirby','Link','Little Mac','Lucario','Lucas',
                'Lucina','Luigi','Mario','Marth','Mega Man','Meta Knight','Mew Two','Mii Swordfighter',
                'Mii Brawler','Mii Gunner','Game and Watch','Ness','Olimar','Pacman','Palutena','Peach',
                'Pikachu','Pit','R.O.B','Robin','Rosalina and Luma','Roy','Ryu','Samus','Sheik','Shulk',
                'Sonic','Toon Link','Villager','Wario','Wii Fit Trainer','Yoshi','Zelda','Zero Suit Samus']


#functions:

#Reply to user requests for character data
def charactername(comment,user_function,no_info,signature,replied_to):
        character= pd.read_csv('%s.csv'%user_function[1].capitalize(), encoding='utf-8')
        if (user_function[1].capitalize() == 'Cloud'): 
                comment.reply('#OP' +'\n  ------------ \n' +signature)
        elif (user_function[1].capitalize() == 'Bayonetta'):
                comment.reply('#(╯ಠ_ಠ）╯︵ ┻━┻' + '\n  ------------ \n' +signature)
        else:
                #Create Kurogane Hammer Link
                kurogane = 'For a glossary of column definitions, please refer to the [Kurogane Hammer Glossary](http://kuroganehammer.com/Glossary)'
                #Reply based on type of character data requested
                #Each class of character data corresponds to one of the tables in Kurogane's website, all NA's are dropped, the table is then prettified, and comment is replied to
                if (user_function[2]=='properties'):
                        properties = character.iloc[:,:4].copy()
                        prettyreply(comment,user_function,properties,kurogane,signature)
                        
                elif(user_function[2]=='ground_moves'):
                        ground_moves=character.iloc[:,4:10].copy()
                        prettyreply(comment,user_function,ground_moves,kurogane,signature)
                        
                elif(user_function[2]=='aerials'):
                        aerials = character.iloc[:,11:20].copy()
                        prettyreply(comment,user_function,aerials,kurogane,signature)
                        
                elif(user_function[2]=='specials'):
                        specials=character.iloc[:,21:27].copy()
                        prettyreply(comment,user_function,specials,kurogane,signature)
                        
                else:
                    comment.reply(no_info)
                    replied_to[comment].append(no_info)
        record(comment, replied_to)
        
def prettyreply(comment, user_function, data, kurogane, signature):
        data = data
        data.dropna(inplace=True)
        pretty=tabulate(data,headers='keys',tablefmt='pipe')
        comment.reply('Smash 4 ' + user_function[1] + ' ' + user_function[2]+': \n\n' + pretty + '\n\n' + kurogane + '\n  ------------ \n' + signature)
        print('replied')

#Reply to requests for lingo definition
def define(comment,user_function,no_info,signature,replied_to, terms):

    #Format user inputs to work with our data
    user_function=user_function[2:]
    for word in range(0,len(user_function)):
        user_function[word]=re.sub('[\W\s\_]','',user_function[word])
        user_function[word]=re.sub('(ing|ly|ed|ious|ies|ive|es|s|ment)?$','',user_function[word])
    user_function= ''.join(user_function)
    user_function=user_function.lower()


    if user_function in terms:
        term_url = requests.get(terms[user_function])
        soup = BeautifulSoup(term_url.text,'html.parser')
        soup_stuff = soup.find('div',{'id':'mw-content-text'})
        soup_stuff = soup_stuff.find('p').get_text()
        comment.reply(soup_stuff +'\n  ------------ \n' + signature)
        replied_to[comment].append(str(soup_stuff))
        print('replied')
    else:
        comment.reply(no_info +'\n  ------------ \n' + signature)
        replied_to[comment].append(no_info)
        print('replied')

    record(comment, replied_to)

#Reply to requests for bot information
def give_info(comment):
        more_info = 'We have over 200k subs on this subreddit, not to mention all the people that see top smash posts. So to all the smashers and spectators, new or old, please feel free to ask me for information.'
        and_more = 'This is a community effort! Thank you to all the contributors at Ssbwiki and of course KuroganeHammer. To see any of the information I provide and more, visit [The Ssbwiki](https://www.ssbwiki.com/) and [Kurogane Hammer](http://kuroganehammer.com/). Also thank you to the mods for allowing me to exist on this awesome sub and hopefully I can be of help around here.'
        comment.reply(signature +'\n  ------------ \n' + more_info + '\n\n' + and_more)
        print('replied')

#Record comments and replies
def record(comment,replied_to):
    with open('records.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(replied_to[comment])
        f.close()

#load terms
with open('terms.csv', 'r',newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    terms = dict((rows[0],rows[1]) for rows in reader)
    f.close()


#create subreddit instance
reddit = praw.Reddit('ssb_bot')

smashbros= reddit.subreddit('test')

#Main script
def main():
    #Empty list that will be populated with user comments from /r/smashbros/new
    user_comments = []
    #In smashbros/new, we look for comments that mention ssb_bot
    for submission in smashbros.hot(limit=25):
        submission.comments.replace_more(limit=0)
        for curr_comment in submission.comments.list():
            if not (curr_comment.body is None) and not (curr_comment.author is None):
                if curr_comment.body.lower().startswith('ssb_bot '):
                    #We want to make sure we haven't yet replied to the current comment. If we have, we skip the addition of the comment
                    if curr_comment.replies.list():
                        i_list = set()
                        for i in curr_comment.replies.list():
                            i_list.add(str(i.author))
                        if ('ssb_bot' not in i_list) and (curr_comment not in user_comments):
                            user_comments.append(curr_comment)
                    #If there are no replies to the current comment, we append it 
                    else:
                        user_comments.append(curr_comment)

    #Empty dict that will be populated with a record of the comment.author, comment.body, and our reply
    replied_to={}
    #For each comment we recorded in the above loop, reply based on the second word of the comment (so index=1)
    for comment in user_comments:
            user_function = comment.body.split(maxsplit=15)
            replied_to[comment]=[str(comment.author),comment.body]
            if (user_function[1].capitalize() in character_list):
                    charactername(comment,user_function,no_info,signature,replied_to)
            if (user_function[1].lower()=='define'):
                    define(comment,user_function,no_info,signature,replied_to,terms)
            elif (user_function[1].lower()=='info'):
                    give_info(comment)
            time.sleep(10)


#Script loop
restart = True
while restart == True:
    try:
        while True:
            restart = False
            main()
            print('going to bed for now')
            time.sleep(120)
    except (RuntimeError,Exception,requests.exceptions.RequestException) as e:
        print(e)
        time.sleep(120)
        restart = True
