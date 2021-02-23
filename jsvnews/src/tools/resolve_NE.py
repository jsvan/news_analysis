#import sqlite3
#import sys
import re
#import spacy
#from collections import Counter
#import en_core_web_sm
#import pprint
import urllib.request
import spacy
import definitions
import os

def cleanBody(body):
    body = body.replace('’', '\'').replace('‘', '\'').replace('…', '...')
    body = body.replace('”', '\"')
    body = body.replace('“', '\"')
    body = body.replace('—', '-').replace('–', '-')
    return body.strip()

cwd = definitions.ROOT_DIR
nlp = spacy.load("en_core_web_sm") #en_core_web_sm.load() #TODO get better/bigger model?
NERs = {'PERSON', 'EVENT', 'ORG', 'GPE', 'NORP', 'LOC', 'PRODUCT', 'WORK_OF_ART', 'LAW', 'LANGUAGE'}
combiningLabels = set(['PERSON', 'ORG'])
best_wiki_guess_no = re.compile(r'>[^<]+?<')
re_title = re.compile(r'<title>.*? - Wikipedia</title>')
wiki_url = "https://en.wikipedia.org/wiki/"
words2resolved_file = os.path.join(cwd, "words2resolved.txt")

fakeNE = set()
realNE = dict()
try:
    with open(words2resolved_file, encoding='utf-8') as F:
        realNE = {x.split(' ')[0]:' '.join(x.split(' ')[1:]) for x in F.read().split('\n')[:-1]}
except FileNotFoundError:
    pass


def save_new_words():
    with open(words2resolved_file, 'w', encoding='utf-8') as F:
        F.write('\n'.join([x + ' ' + y for x, y in realNE.items()]) + '\n')


def just_wiki_it(it):
    it = it.replace('\xa0', '_').replace(' ', '_').strip()
    b = 0
    e = len(it)
    # Breaks with
    # 'Four of our team will be fighting': Khabib says UFC 254 comeback will be family affair

    # This cuts off all leading and trailing non alphas ?
    while  b<e and not it[b].isalpha():
        b += 1
    while e>b and not it[e - 1].isalpha():
        e -= 1
    it = it[b:e]

    if it.lower().startswith('the_'):
        it = it[4:]
    if it.endswith('\'s'):
        it = it[:-2]

    if it in fakeNE:
        return
    if it in realNE:
        return realNE[it]

    try:
        response = urllib.request.urlopen(wiki_url + urllib.parse.quote(it))
        title = ''
        for i in response:
            i = i.decode("utf-8")
            # if '>Look up <' in i:
            if '<title>' in i:
                title = re_title.search(i).group()[7:-20]
                # if 'Wikipedia articles witwwwh ' in i:
                # if 'class="mw-redirect"' in i:
                """
                if '80px-Wiktionary-logo-en-v2.svg.png 2x' in i:
                # NOT FOUND TAKE BEST GUESS
                #best_wiki_guess = best_wiki_guess_no.search(i).group()[1:-1]
                print('BG ', best_wiki_guess)
                else:"""
                best_wiki_guess = title
                realNE[it] = cleanBody(title)
                return best_wiki_guess

    except urllib.error.HTTPError as e:
        fakeNE.add(it)
    except urllib.error.URLError as e:
        print(e)
    except AttributeError as e:
        print(e, e.__doc__)
    return

from pprint import pprint
# condenses the various named entities into a single universal unit


def jprint(tp, bo):
    if False: #replace with bo
        pprint(tp)


#TODO Possible bug if removed item is still used to compare and consolidate, when longerone should be used.
def kondenz_milch(t):
    tuplist = t
    #pprint(tuplist)
    #print('\n\n')
    for i in range(len(tuplist)):
        for j in range(len(tuplist)):
            if i is j:
                continue
            if not (tuplist[i] and tuplist[j]):
                continue
            if not (tuplist[i]['label'] in combiningLabels and tuplist[j]['label'] in combiningLabels):
                continue
            if len(tuplist[i]['text']) > len(tuplist[j]['text']):
                if tuplist[j]['text'] in tuplist[i]['text']:
                    tuplist[i]['count'] += tuplist[j]['count']
                    tuplist[i]['locations'] += tuplist[j]['locations']
                    tuplist[j] = []
            else:
                if tuplist[i]['text'] in tuplist[j]['text']:
                    tuplist[j]['count'] += tuplist[i]['count']
                    tuplist[j]['locations'] += tuplist[i]['locations']
                    tuplist[i] = []
    #print('\n\n')
    #pprint(tuplist)
    return tuplist


def process_article(a):
    article = nlp(a)
    t = [dict([('text', x.text),
               ('label', x.label_),
               ('locations', [(x.start, x.end)]),
               ('count', 1)])
         for x in article.ents if x.label_ in NERs]
    finallist = []
    kondenz_milch(t)
    for i in kondenz_milch(t):
        if i:
            i['text'] = just_wiki_it(i['text'])
            if i['text']:
                finallist.append(i)
    finalmap = []  # (0,0,'')
    for i in finallist:
        for l in i['locations']:
            finalmap.append((l[0], l[1], i['text']))
    finalmap.append((len(article), len(article), ''))
    finalmap.sort()
    #Should I be grabbing all nouns? gets complicated fast
    #print('FM',finalmap)
    save_new_words()
    return [x.text for x in article], finalmap

    """
    Returning
    [The, trouble, at, the, UN, went, far, beyond, the, WHO, ,, however, ., In, 2016, ,, Anthony, Banbury, ,, a, career, UN, official, who, had, recently, served, as, assistant, secretary, -, general, for, field, support, ,, wrote, that, the, organization, ’s, bureaucracy, had, become, so, complex, that, it, was, incapable, of, delivering, results, ,, creating, a, black, hole, into, which, disappeared, “, countless, tax, dollars, ,, ”, as, well, as, a, long, list, of, “, human, aspirations, ,, never, to, be, seen, again, ., ”, Such, lost, opportunities, have, led, to, cynicism, and, have, weakened, the, liberal, international, order, from, within, .]
    [(4, 5, 'United Nations'), (9, 10, 'World Health Organization'), (16, 18, 'Anthony Banbury'), (21, 22, 'United Nations'), (102, 102, '')]
    
    The list of the article separates tokenizes punct -- matches up with the finalmap 
    """



    """
    print(finalmap)
    # print(article.text)
    print('~~~\n')
    strlist = []
    endprevious = 0
    # article=article.text
    for loc in finalmap:
        strlist.append(article[endprevious:loc[0]].text + ' \x1b[1;9m' + article[loc[0]:loc[
            1]].text + '\x1b[0m ' + ' \x1b[1;102m' + loc[2] + '\x1b[0m ')
        endprevious = loc[1]
    
    for loc in finalmap:
        strlist.append('>>>'+article[endprevious:loc[0]].text + ' ' + loc[2] + '<<< ')
        endprevious = loc[1]
    finalarticle = ''.join(strlist)
    #sys.stdout.write(finalarticle)
    #print('\n')
    ### I don't have to replace the words. I should mark where the NE belong in the text. 
    """
