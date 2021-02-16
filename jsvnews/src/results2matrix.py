import os
words2resolved_file = "words2resolved.txt"
with open(words2resolved_file, encoding='utf-8') as F:
    NE2idx = {' '.join(x.split(' ')[1:]):i for i, x in enumerate(F.read().split('\n')[:-1])}
print(f'we have {len(NE2idx)} named entities!')

monthMap = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09','October':'10', 'November':'11', 'December':'12',
            'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09','Oct':'10', 'Nov':'11', 'Dec':'12'}

def itemGenerator(batch_dir, suffix, divider):
    fs = [x for x in os.listdir(batch_dir) if x.endswith(suffix)]
    fs.sort()
    for f in fs:
        for X in open(os.path.join(batch_dir, f), encoding='utf-8'):
            yield X.strip().split(divider)
        # Yields example ['POS', "NEG"]

def add_triple(where, what):
    return [where[0] + what[0],
            where[1] + what[1],
            where[2] + what[2]]

def ensure_pub_ent(dic, pub, day, art, ent):
    # want  {publisher: {date: {article#: {named_entity: [neg,neu,pos]}}}}
    if pub not in dic:
        dic[pub] = dict()
    if day not in dic[pub]:
        dic[pub][day] = dict()
    if art not in dic[pub][day]:
        dic[pub][day][art] = dict()
    if ent not in dic[pub][day][art]:
        dic[pub][day][art][ent] = [0, 0, 0]

def save_matrices(out_dir, to_matrix, save_sentences):
    """
    saves matrices to daily folder of publisher
        out_file looks like ./data/matrices
            will need to expand to ./data/matrices/nyt/today/matrix.pkl
        to_matrix looks like  {DATE: {PUBLISHER: {article: {named_ent: [1,2,3]}}}}
    """
    import os
    from jsvnews.src.tools.sparse_matrix import jsv_dictmat
    for today in to_matrix.keys():
        for publisher in to_matrix[today].keys():
            if not today:
                print(publisher)
                continue
            # make the publisher path
            pub_path = os.path.join(out_dir, publisher)
            if not os.path.isdir(pub_path):
                os.system(f"mkdir {pub_path}")
            # if date is in wrong order bc reading from a database, gotta reshuffle the parts around.
            # Want YYYY-MM-DD
            wTdy = today.split('-')
            print(wTdy)
            if len(wTdy[2]) == 4:  # HAX for if YYYY is at the end
                wTdy = f"{wTdy[2][:4]}-{monthMap[wTdy[1]]}-{wTdy[0]}"
            elif ',' in wTdy[1] and len(wTdy[2]) > 7 and ':' in wTdy[2]:  # handle SINA news shit
                wTdy = f"{wTdy[1][-4:]}-{monthMap[wTdy[0]]}-{wTdy[1].split(',')[0]}"
            else:
                wTdy = '-'.join(wTdy)
            print(wTdy)
            matrix_path = f'{os.path.join(pub_path, wTdy)}.pkl'
            #if os.path.isfile(matrix_path):
            sparse = jsv_dictmat(matrix_path) if os.path.isfile(matrix_path) else jsv_dictmat()  # TODO DEBUG: Make sure this works as expected
            for article in to_matrix[today][publisher].keys():
                sparse.from_model_output(to_matrix[today][publisher][article])  # sending all named_ents to the sparse
            print(f"Saving {publisher} to {matrix_path}")
            sparse.save(matrix_path)
            print("Completed saved.")
    with open(f"{out_dir}-all-guesses-{wTdy}.txt", 'w', encoding='utf-8') as F:
        F.write('\n'.join(save_sentences))

def run(batch_dir, out_dir):
    #Generator
    labels = itemGenerator(batch_dir, '-labels', '\t\t')
    #Generator
    sentences = itemGenerator(batch_dir, '.txt', '####')

    import re
    # to_matrix will be {publisher: {article#: {named_entity: [neg,neu,pos]}}}
    to_matrix = dict()
    save_sentences = []
    sentGen, labGen = False, False
    newspaper, url, timepublished = '','',''
    # while more lines of articles, model labels are available...
    artcount = -1
    while True:
        # sentence, labs = '', ''
        sentGen, labGen = False, False
        try:
            sentence = sentences.__next__()[0]
            sentGen=True
            if sentence.startswith('JSVSRC: '):  # arrived at start line of new article
                artcount += 1
                # that means we got: f'JSVSRC:  {art["newspaper"]}  {art["url"]}  {art["timepublished"]}' time:  Tue, 29 Dec 2020 17:58:31 +0300
                art = sentence.split('  ')  # double spaces
                newspaper, url, timepublished = art[1], art[2], art[3]
                timepublished = '-'.join(timepublished.split(' ')[1:4])

            labs = labels.__next__()
            labGen=True
            matches = [m for m in re.finditer('\[\[.+?\]\]', sentence)]
            if matches:
                prev = 0
                for ii, m in enumerate(matches):
                    if ii >= len(labs):
                        break

                    sentence = sentence.replace(m.group(), m.group()[:-2]+'|'+labs[ii]+']]', 1)
                    NE = NE2idx[m.group()[2:-2]]  # get rid of brackets ie: "[[stuff]]"
                    ensure_pub_ent(to_matrix, timepublished, newspaper, artcount, NE)  # (dic, pub, art, ent)
                    if labs[ii] == 'NEG':
                        to_matrix[timepublished][newspaper][artcount][NE][0] += 1
                    elif labs[ii] == 'NEU':
                        to_matrix[timepublished][newspaper][artcount][NE][1] += 1
                    else:  # label is "POS"
                        to_matrix[timepublished][newspaper][artcount][NE][2] += 1
            save_sentences.append(sentence)
        except StopIteration:
            try:
                if not sentGen:  # sentences not still available
                    labs = labels.__next__()  # Try if labels still available
                    labGen = True
            except StopIteration:
                print("Triggered stopiteration label extra")
                pass
            print("Sentences still available?  {}  {}\nLabels still available? {}  {}".format(sentGen, sentence, labGen, labs))
            break

    save_matrices(out_dir, to_matrix, save_sentences)