import os
import pickle
import time



def mkdir(pathlist):
    # makes the directory and all parent directories, even though there's a builtin sh flag to do so.
    path = ''
    for p in pathlist:
        path = os.path.join(path, p)
        if not os.path.isdir(path):
            os.system(f'mkdir {path}')
            print(f"made directory {path}")

def resetdir(path, files):
    print(f"Erasing {files} from {path}")
    if not files:
        files = os.listdir(path)
    for f in files:
        try:
            os.remove(os.path.join(path, f))
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
    print("Erasing all bloat directories")
    toclean = [('gmail_in', []),  # *
               ('gmail_out', []),  # *
               ('bert_train_in', ['dev.txt','test.txt','train.txt']),
               ('bert_process_loading_in', [])]

    for d, fs in toclean:
        resetdir(filepaths[d], fs)




TIME_FILE = 'last_run_times.pkl'
FILE_FILE = 'filepaths.txt'
EPSILON = 10  # seconds
ONE_HOUR = 3600
TWENTY_FOUR_HOURS = (24 * ONE_HOUR) - EPSILON
ONE_WEEK = (24 * 7 * ONE_HOUR) - EPSILON
FORCE_TRAIN = False
FORCE_SPIDER = True
RESET = False
READDATABASE = 'articlesstormtrooper.db'
try:
    with open(TIME_FILE, 'rb') as F:
        timings = pickle.load(F)
except FileNotFoundError:
    timings = {'TRAIN':  0,
               'SPIDER': 0}

# keys: 'gmail_in', 'gmail_out', 'bert_in', 'bert_out', 'matrix_out'
with open(FILE_FILE) as F:
    fps = [x.split('#')[0].split(' ') for x in F.read().split('\n') if x]
    filepaths = {x[0][:-1]:os.path.join(*x[1:]) for x in fps}

for x in fps:
    mkdir(x[1:])


if RESET:
    reset_all_dirs(filepaths)




# TODO: Delete all temporary files after using them

#  ~~~ TRAINING ~~~
#  Grabs jsvsentilabel@gmail.com datapoints and trains on ALL points -- every 7 days

start_time = time.time()
print("Checking time")

if FORCE_TRAIN or (start_time - timings['TRAIN']) >= ONE_WEEK:
    print("Within a week. Training!")

    # put jsvsentilabel@gmail emails into ./emailscripts/datafiles
    print("Importing gmail")
    from jsvnews.src.emailscripts import gmail
    print("Running gmail")
    gmail.run(filepaths['gmail_in'], filepaths['gmail_out'], filepaths['info_dir'])
    
    # Creates train test sets
    print("importing create-train0-test-dev")
    from jsvnews.src.emailscripts import create_train_test_dev
    print("Running cttd")
    create_train_test_dev.run(filepaths['gmail_out'], filepaths['homemade_data'], filepaths['bert_train_in'])

    # run training
    print("training model")
    os.chdir(filepaths["bert_location"])
    print('dir:')
    os.system('dir')
    os.system("sh train.sh")
    print("Finished training")
    os.chdir(filepaths["get_home"])
    timings['TRAIN'] = start_time

    with open(TIME_FILE, 'wb') as F:
        pickle.dump(timings, F)



time.sleep(3)


# ~~~ SPIDER ~~~

start_time = time.time()
if FORCE_SPIDER or (time.time() - timings['SPIDER']) >= TWENTY_FOUR_HOURS:
    # Grabs news articles and places into database -- should be every 12 hours
    # use dok_matrix()
    # Make a matrix of every day of news
    #

    resetdir(filepaths['bert_process_loading_in'], [])

    print("PROCESS LOOP")
    from jsvnews.src import process_loop
    process_loop.run(out_file=filepaths['bert_process_loading_in'],
                     feedlist=os.path.join(filepaths['rssfeedlist'], 'rssfeeds.txt')) #, fromdatabase=READDATABASE)

    # TODO: Create script: converts news articles into sentiment matrices
    # Put news articles into emailscripts/newssource
    # Run unprocessed article text through model
    # Run the model on prepared articles

    print("BERT PROCESS BATCHES")
    from jsvnews.src import bert_process_batch
    #BERT_DIR, HOME_DIR, BATCH_DIR, BERT_IN_DIR, BERT_OUT_FILE
    bert_process_batch.run(BERT_DIR=filepaths['bert_location'],
                           HOME_DIR=filepaths['get_home'],
                           BATCH_DIR=filepaths['bert_process_loading_in'],
                           BERT_IN_DIR=filepaths['bert_process_in'],
                           BERT_OUT_FILE=os.path.join(filepaths['bert_process_out'], 'labels.txt' ))

if True:
    print("RESULTS 2 MATRICES")
    # associate articles with sentiment scores
    from jsvnews.src import results2matrix
    results2matrix.run(filepaths['bert_process_loading_in'],
                       filepaths['matrix_out'])

    # TODO: Create profile system: Update profiles with sentiment matrices
    # TODO: Store compressed daily matrices
    timings['SPIDER'] = start_time

if RESET:
    reset_all_dirs(filepaths)

with open(TIME_FILE, 'wb') as F:
    pickle.dump(timings, F)
