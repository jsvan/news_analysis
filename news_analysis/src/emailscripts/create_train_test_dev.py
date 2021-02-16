import os
from transformers import BertTokenizer
import random

if not os.path.isdir(os.path.join( "news_analysis", "ABSA_BERT_MODEL", "data")):
    raise NotADirectoryError(os.path.join( "news_analysis", "ABSA_BERT_MODEL", "data") )

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True, cache_dir=os.path.join( 'ABSA_BERT_MODEL', "cache"))


def cleanBody(body):
    body = body.replace('’', '\'').replace('‘', '\'').replace('…', '...')
    body = body.replace('”', '\"')
    body = body.replace('“', '\"')
    body = body.replace('—', '-').replace('–', '-')
    return body.strip()


def mask(sentence, df):
    lab = []
    sentence = cleanBody(sentence)
    for word in sentence.split(' '):
        if '[POS]' in word:
            lab.append('T-POS')
        elif '[NEG]' in word:
            lab.append('T-NEG')
        elif '[NEU]' in word:
            lab.append('T-NEU')
    masked = tokenizer.tokenize(sentence.replace("[POS]", "[MASK]").replace("[NEU]", "[MASK]").replace("[NEG]", "[MASK]"))
    counter = 0
    labels = []
    try:
        for item in masked:
            if item == '[MASK]':
                labels.append(item+'='+lab[counter])
                counter += 1
            else:
                labels.append(item+'=O')
    except IndexError:
        print("error with:")
        print(df, sentence)
        return ''
    return ' '.join(masked) + "####" + ' '.join(labels)




def run(datafilesdir, homemadedir, destfolder):
    allitems = []
    """ to_process = os.listdir(homemadedir)
    for df in to_process:
        print("Reading ", df)
        with open(os.path.join(homemadedir, df), encoding='utf-8') as F:
            allitems += [mask(x, df) for x in F.read().split('\n')[:-1]]
    """
    to_process = os.listdir(datafilesdir)
    for df in to_process:
        if not df.endswith('processed'):
            # foreign language, skip
            continue
        print("Reading ", df)
        with open(os.path.join(datafilesdir, df), encoding="utf-8") as F:
            allitems += [mask(x, df) for x in F.read().split('\n')[:-1]]

    random.shuffle(allitems)
    if not os.path.isdir(destfolder):
        os.system("mkdir "+destfolder)

    with open(os.path.join(destfolder, "train.txt"), 'w', encoding='utf-8') as F:
        F.write('\n'.join(allitems))

    with open(os.path.join(destfolder, "test.txt"), 'w', encoding='utf-8') as F:
        F.write('\n'.join(allitems[:2] ))

    with open(os.path.join(destfolder, "dev.txt"), 'w', encoding='utf-8') as F:
        F.write('\n'.join(allitems[2:4] ))

  #  We love the pink pony.####we=O love=O the=O pink=T-POS pony=T-POS .=O
  #  We love the [MASK].####we=0 love=0 the=0 [MASK]=T-POS .=0