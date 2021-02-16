import os, re
from datetime import date
from sys import exit as sexit
import pickle
TODAY = date.today().__str__()
SAVEDIR = os.path.join('data', 'homemade')
SAVEFILE = os.path.join(os.path.join(SAVEDIR, f"{TODAY}.txt"))
CONFFILE = os.path.join(SAVEDIR, "confusion_matrix.pkl")
OFFSET = 0
print(f"Today is {TODAY}")
try:
    os.mkdir(SAVEDIR)
except FileExistsError:
    pass

with open("filepaths.txt") as F:
    fps = [x.split('#')[0].split(' ') for x in F.read().split('\n') if x]
    filepaths = {x[0][:-1]:os.path.join(*x[1:]) for x in fps}

#fpn = [x for x in os.listdir('data') if x.endswith('.txt') and x.startswith('matrices-all-guesses')]
FPN = os.path.join('data', f'matrices-all-guesses-{TODAY}.txt')

def save_confusion(conf):
    with open(CONFFILE, 'wb') as F:
        pickle.dump( conf, F)
    print("saved confusion matrix")


def load_confusion():
    if os.path.isfile(CONFFILE):
        with open(CONFFILE, 'rb') as F:
            conf = pickle.load(F)
    else:
        conf = [["  ", "M-", "M*", "M+", "!M"],
                ["A-", 0, 0, 0, 0],
                ["A*", 0, 0, 0, 0],
                ["A+", 0, 0, 0, 0]]
    print_results(conf)
    return conf

def model_output():
    with open(FPN, encoding='utf-8') as F:
        for line in F:
            if not line.startswith("JSVSRC"):
                yield line.strip()

def save(tosave, conf):
    if not tosave:
        print("Not saving, nothing to save.")
        return
    prefix = '\n' if os.path.isfile(SAVEFILE) and tosave else ''
    with open(SAVEFILE, 'a', encoding='utf-8') as F:
        F.write(prefix + '\n'.join(tosave))

    print(f"Saved in {SAVEFILE}")
    save_confusion(conf)

def convert(sentence):
    """
        matches = [m for m in re.finditer('\[\[.+?|', sentence)]
    for m in matches:
        start, end = m.span()
        sentence = f"{sentence[:start]}[[{sentence[end:]}"
    return sentence
    :param sentence:
    :return:
    """
    return re.sub('\[\[.+?\||\[\[[^\|]+?\]\]', '[[[', sentence), re.findall('\|.+?\]\]|\[\[[^\|]+?\]\]', sentence)

def replace(sentence, listoflabels):
    """
    not efficient -- don't care.
    :param sentence:
    :param listoflabels:
    :return:
    """
    for i in listoflabels:
        sentence = re.sub('\[\[\[.+?\]\]', f"[[{i}]]", sentence, 1)
    return sentence

def midx(label):
    label = label.lower()
    if label == 'neg':
        return 1
    if label == 'neu':
        return 2
    if label == 'pos':
        return 3
    if label == 'na':
        return 4
    raise ValueError(f"{label} not neg, neu, or pos error")


def jprint(line):
    maxlen = 150
    prev = 0
    while prev < len(line):
        newend = min(len(line), prev+maxlen)
        print(line[prev:newend])
        prev += maxlen


def print_results(confusion_matrix):
    print()
    total, correct= 0,0
    for x in range(1, len(confusion_matrix)):
        for y in range(1, len(confusion_matrix[x])):
            total += confusion_matrix[x][y]
            if x == y:
                correct += confusion_matrix[x][y]

    print(f"{correct}/{total} = {100 * float(correct) / total:.4}% correct")
    for row in confusion_matrix:
        print('\t'.join([str(x) for x in row]))
    print()


def help():
    print()
    print("<ENTER> to mark item as correct")
    print("<INTEGER> to skip that many entries forward" )
    print("('n' | 'neg', 'k'|'neu', 'p'|'pos')")
    print("('x' | 'skip') to skip line")
    print("('m' | 'matrix' | 'mat') to show confusion matrix")
    print("('s' | 'save') to save and end.")
    print("('h' | 'help') to see these options again")
    print("('r' | 'reveal') to repeat prompt line.")
    print()

def run():
    print("Welcome to self scoring.")
    help()
    gmap = {'n':'NEG', 'k':'NEU', 'p':'POS', 'neg':'NEG', 'neu':'NEU','pos':'POS'}
    newpoints = []
    # Want to create samples in form of
    # "Just last month, both [NEG] and [NEG] reported over 10 million total cases in their regions. The [NEG] alone has over 9 million cases with a rapidly accelerating outbreak."
    overi = 0
    confusion_matrix = load_confusion()
    lines = model_output()
    line=lines.__next__()
    while True:
        try:
            line = lines.__next__()
        except StopIteration:
            print("Saving and Ending")
            save(newpoints, confusion_matrix)
            print_results( confusion_matrix)
            newpoints.clear()
            break
        # Outputs "Whatever benefits [[Joe Biden|NEG]] might see in buckling to [[Iran|NEG]]'s extortion , the risks and potential costs should also be apparent."
        sentence, guessed = convert(line)
        jprint(f"{overi}) {sentence}")
        i = 0
        known = []
        while i < len(guessed):
            mguess = guessed[i][1:-2]
            if mguess.lower() not in gmap:
                mguess = 'na'
            guess = mguess
            back = input(f"\t{i}) {mguess}?\t-->\t").lower()
            if back in gmap:
                guess = gmap[back]
                confusion_matrix[midx(guess)][midx(mguess)] += 1
            elif back == 's' or back == 'save':
                save(newpoints, confusion_matrix)
                newpoints.clear()
                continue
            elif back == 'e' or back == 'end':
                print("Saving and Ending")
                save(newpoints, confusion_matrix)
                newpoints.clear()
                print_results( confusion_matrix)
                sexit()
            elif back == 'r' or back == 'reveal':
                print(line)
                continue
            elif back == 'x' or back == 'skip':
                i += 1000
                continue
            elif back =='m' or back =='mat' or back=='matrix':
                print_results( confusion_matrix)
                continue
            elif back =='help' or back == 'h':
                help()
                continue
            elif back.isdigit():
                for iii in range(int(back) - 1):
                    line = lines.__next__()
                    overi += 1
                known.clear()
                break
            elif back:
                print("Try again, input not understood")
                help()
                continue
            elif not back:
                confusion_matrix[midx(guess)][midx(mguess)] += 1
            known.append(guess)
            i += 1
        if known:
            newpoints.append(replace(sentence, known))
        overi += 1



run()