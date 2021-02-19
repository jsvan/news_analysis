from jsvnews.database import mydb
from jsvnews.src.tools import resolve_NE
from string import ascii_uppercase
import langdetect
import os

LIMIT = " "  # "LIMIT 10" Optional, default is ""
DATASET_NAME = os.path.join("C:","Users","onion","PycharmProjects","jsvnews","database","dbs","censored_titles_set")
# open(DATASET_NAME, 'w').close()  # Make sure got path okay
CENSOR_NAMES = ascii_uppercase
dataset = []

def get_censor_name(i,text):
    # just point them out
    return " [[" + text + "]]"
    i = i % len(CENSOR_NAMES)
    return f' [{CENSOR_NAMES[i]}{CENSOR_NAMES[i]}]'

def pull_text():
    db, c = mydb.DB().on_start()
    nw = c.execute("SELECT id, name FROM newspaper_tbl;")  # title, timepublished
    nw = nw.fetchall()
    newspapers = {n[0]: n[1] for n in nw}
    print(newspapers)
    gettitles = c.execute("SELECT title, text, websitename, timepublished FROM article_tbl" + LIMIT + ';')  # title, timepublished

    return gettitles, newspapers


def censor_titles(dbpull, newspapers):
    S = Saver()
    for ii, item in enumerate(dbpull):
        #if random.random() < 0.70:
        #    continue
        #if 'Trump' not in item[1]:
        #    continue
        if '((' in item[1]:  #gotta take out all ((Mozambique:Mozambique)) such that i did. Too lazy for now.
            continue
        if not item and not item[1]:
            continue
        try:
            if langdetect.detect(item[1]) != 'en':
                continue
        except langdetect.lang_detect_exception.LangDetectException:
            continue

        print(ii, end='\r')
        i = '\n'.join([ item[0], item[1]])
        titletext, titlemap = resolve_NE.process_article(i)
        censored_title = []
        endprevious = 0
        for e, (start, end, text) in enumerate(titlemap):
            if not text:
                continue
            censored_title.append(' '.join(titletext[endprevious:start]) + get_censor_name(e,text))  # Spaced as "X X X X"
            endprevious = end

        if censored_title:
            censored_title.append(' '.join(titletext[endprevious:]))
            S.save('\n'.join([newspapers[item[2]], item[3], ' '.join(censored_title)]))
    # Should only contain titles with NE within

class Saver:
    totalcount = 0

    def save(self, article):
        #print("SAVING:")
        with open("C:\\Users\\onion\\PycharmProjects\\jsvnews\\database\\dbs\\censored_titles_set\\" + str(Saver.totalcount) + '.txt', 'w', encoding='utf-8') as F:
            #print("Saved", str(Saver.totalcount))
            F.write(article)
            Saver.totalcount += 1



print("Pulling text")
t, newspapers = pull_text()

print("Censoring Titles")
ds = censor_titles(t, newspapers)
#print("Saving dataset")
#save_dataset(ds)
print("finished! :)  Written to", DATASET_NAME)
