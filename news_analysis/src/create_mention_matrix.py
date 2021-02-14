from database.code import mydb
from src.tools import resolve_NE
import langdetect
import numpy as np
import time
import pickle
import datetime

LIMIT = 1500  # "LIMIT 10" Optional, default is ""
dataset = []
num2dbwebsite = dict()
websitemap = dict()
NEmap = dict()
matrix = []


def pull_text(c):
    if LIMIT > 0:
        L = " LIMIT "+str(LIMIT)
    gettitles = c.execute("SELECT title, text, websitename FROM article_tbl" + L + ';')  # title, timepublished
    return gettitles


def pull_website(c):
    gettitles = c.execute("SELECT id, name FROM newspaper_tbl;")  # title, timepublished
    return gettitles.fetchall()


def pull_text_count(c):
    if LIMIT > 0:
        return LIMIT
    else:
        count = c.execute("SELECT COUNT(*) FROM article_tbl;")  # title, timepublished
        return count.fetchall()[0][0]


def get_mentions(article, sitename, articlecolumn):
    # MAKE SURE IS ENGLISH
    try:
        if langdetect.detect(article) != 'en':
            return
    except langdetect.lang_detect_exception.LangDetectException:
        # This occurs if the sentence has no letters (just numbers etc)
        # or other bullshit == bad sentence -> ignore
        return

    if 'Trump' not in article:
        return

    _, mentions = resolve_NE.process_article(article)

    # Add the new row to website map
    # Websitemap points to this new article row
    websitemap[sitename].append(articlecolumn)

    # Add new article row
    # Corresponding to single article...
    for i in mentions:
        NE = i[2]
        NEnum = map_NE(NE)
        # print('siteid {}, NEnum {}, len(mat) {}, len(mat[0]) {} '.format(sitename, NEnum, len(matrix), len(matrix[0])))
        matrix[NEnum][articlecolumn] += 1


def map_NE(name):
    # Makes sure row is in matrix
    # Gives you that row
    if name not in NEmap:
        NEmap[name] = len(NEmap)
        matrix.append([0]*ARTICLECOUNT)
    return NEmap[name]


def prepare_websitenames(c):
    # Map foreignkey to websitename
    allnames = pull_website(c)
    for id, site in allnames:
        num2dbwebsite[id] = site


def map_website(c, name):
    # Map foreignkey to websitename
    name = num2dbwebsite[name]
    # Map websitename to array of articles/row
    if name not in websitemap:
        websitemap[name] = []
    return name


"""
    
    [ T [[A][R][T][I][C][A][L][ ][C][O][U][N][T]]
      O [                                       ]
      P [                                       ]
      I [                                       ]
      C [                                       ]
      
      C [                                       ]
      O [                                       ]
      U [                                       ]
      N [                                       ]
      T [[0][0][0][0][0][0][0][0][0][0][0][0][0]]
      
"""


DBclass = mydb.DB()
db, c = DBclass.on_start()

ARTICLECOUNT = int(pull_text_count(c))
print("Processing {} articles.".format(ARTICLECOUNT))

prepare_websitenames(c)
dbpull = pull_text(c)
t0 = time.time()
for i, entry in enumerate(dbpull):
    print("{}/{}          elapsed time {}".format(i, ARTICLECOUNT, datetime.timedelta(seconds=int(time.time()-t0))), end='\r')
    websitenum = map_website(c, entry[2])
    titlearticle = entry[0]+entry[1]
    get_mentions(titlearticle, websitenum, i)

# Grieg lyric pieces op54 nocturne
print("\n\nFinished, converting to numpy")
matrix = np.array(matrix)
print("Beginning saving")
np.save("mention_matrix.npy", matrix)
pickle.dump(NEmap, open("mention_NEmap.pkl",'wb') )
pickle.dump(websitemap, open("mention_websitemap.pkl",'wb') )
DBclass.on_end()
print("Finished!")
