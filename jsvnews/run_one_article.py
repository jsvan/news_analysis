import os
import pickle
import time
import definitions
import sys
from jsvnews.src.tools.getNews import Scraper
"""
This file is just like run.py, but it takes a single URL as input, and it does the whole pipeline on it.
"""

verbose = True
cwd = definitions.ROOT_DIR

if verbose:
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.abspath(__file__))
    print("root", cwd)


def mkdir(pathlist):
    # makes the directory and all parent directories, even though there's a builtin sh flag to do so.
    path = ''
    for p in pathlist:
        path = os.path.join(path, p)
        if not os.path.isdir(path):
            os.system(f'mkdir {path}')
            if verbose:
                print(f"made directory {path}")

def resetdir(path, files):
    if verbose:
        print(f"Erasing {files} from {path}")

    if not files:
        files = os.listdir( path)
    for f in files:
        try:
            os.remove(os.path.join( path, f))
        except FileNotFoundError:
            continue


def reset_all_dirs(filepaths):
    # empty [] means delete all files
    # TODO figureout which files to delete
    """
    gmail_in: data emails raw
    gmail_out: data emails prepared
    contribution_count: data emails
    bert_location: lib ABSA_BERT_MODEL
    get_home: .. ..#This is the inverse of "bert_location"
    bert_train_in: lib ABSA_BERT_MODEL data commonsents
    bert_process_loading_in: data bert_in
    bert_process_in: lib ABSA_BERT_MODEL data newsprepared# process_loop.py out, bert work.py in
    bert_process_out: lib ABSA_BERT_MODEL data newsprepared outputs
    matrix_out: data matrices# (will be data/matrices/publisher/day/ and THEN matrix_file. Matrix made from )
    rssfeedlist: src# rssfeeds.txt

    :param filepaths:
    :return:
    """
    if verbose:
        print("Erasing all bloat directories")

    toclean = [('gmail_in', []),  # *
               ('gmail_out', []),  # *
               ('bert_train_in', ['dev.txt','test.txt','train.txt']),
               ('bert_process_loading_in', [])]

    for d, fs in toclean:
        resetdir(filepaths[d], fs)



FILE_FILE = os.path.join(cwd, 'jsvnews','utilities', 'filepaths.txt')

RESET = False

# keys: 'gmail_in', 'gmail_out', 'bert_in', 'bert_out', 'matrix_out'

def run(url):
    if verbose:
        print('i am',os.path.dirname(sys.executable))
        print('or', os.path.dirname(os.path.realpath(__file__)))
        print(os.listdir())

    with open(FILE_FILE) as F:
        fps = [x.split('#')[0].split(' ') for x in F.read().split('\n') if x]
        filepaths = {x[0][:-1]:os.path.join(cwd, *x[1:]) for x in fps}

    for x in fps:
        mkdir(cwd.split(os.path.sep) + x[1:])


    if RESET:
        reset_all_dirs(filepaths)


    start_time = time.time()

    resetdir(filepaths['bert_process_loading_in'], [])

    print("PROCESS LOOP")
    article_scraper = Scraper()
    article_body = Scraper.scrape_url(url)
    process_loop.run(out_file=filepaths['bert_process_loading_in'],
                     feedlist=os.path.join(filepaths['rssfeedlist'], 'rssfeeds.txt')) #, fromdatabase=READDATABASE)

    print("BERT PROCESS BATCHES")
    from jsvnews.src import bert_process_batch
    #BERT_DIR, HOME_DIR, BATCH_DIR, BERT_IN_DIR, BERT_OUT_FILE
    bert_process_batch.run(BERT_DIR=filepaths['bert_location'],
                           HOME_DIR=filepaths['get_home'],
                           BATCH_DIR=filepaths['bert_process_loading_in'],
                           BERT_IN_DIR=filepaths['bert_process_in'],
                           BERT_OUT_FILE=os.path.join(filepaths['bert_process_out'], 'labels.txt' ))

    print("RESULTS 2 MATRICES")
    # associate articles with sentiment scores
    from jsvnews.src import results2matrix
    results2matrix.run(filepaths['bert_process_loading_in'],
                       filepaths['matrix_out'])

    # TODO: Create profile system: Update profiles with sentiment matrices
    # TODO: Store compressed daily matrices

