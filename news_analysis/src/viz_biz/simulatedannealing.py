import os
from src.tools.sparse_matrix import jsv_dictmat
from math import sqrt
from random import gauss, random, randint
from math import exp
ITERATIONS = 10000000



class lookup_mat:
    """
    makes matrix of topic x topic, filled with proportion of articles that include both topics.
    """
    def addtocounts(self, a, b):
        if a not in self.counts:
            self.counts[a] = 0
        if b not in self.counts:
            self.counts[b] = 0
        self.counts[a] += 1
        self.counts[b] += 1


    def __init__(self, M):
        self.lookup = dict()
        self.numarticals = len(M)
        self.counts = dict()
        print("Building lookup matrix")
        for i, article in enumerate(M):
            print(i, len(M), end='\r')
            topics = list(article[1])
            for top0idx in range(len(topics)):
                for top1idx in range(top0idx, len(topics)):
                    # For every unique combination of mentioned topics in an article...
                    top0, top1 = topics[top0idx], topics[top1idx]
                    self.addtocounts(top0, top1)
                    # Get them into a standard (numerical) order...
                    if top0 > top1:
                        top0, top1 = top1, top0
                    if top0 not in self.lookup:
                        self.lookup[top0] = dict()
                    if top1 not in self.lookup[top0]:
                        self.lookup[top0][top1] = 0
                    self.lookup[top0][top1] += 1

    def get(self, top0, top1):
        # Given youre talking about top0, how likely is it to see top1
        try:
            c = self.counts[top0]
            if top0 > top1:
                top0, top1 = top1, top0
            return self.lookup[top0][top1] / c
        except KeyError:
            return 0

    def getrange(self, T, idxsrc, idxdest):
        maxcount = 10
        tots = 0.0
        c = 1
        totdiv = 0
        # go left
        while(idxdest - c >= 0 and c <= maxcount):
            # divide by c to downweight further items
            tots += self.get(T[idxsrc], T[idxdest-c]) * (maxcount - c)/maxcount
            c += 1
            totdiv += 1
        c = 1
        while(idxdest + c < len(T) and c <= maxcount):
            tots += self.get(T[idxsrc], T[idxdest+c]) * (maxcount - c)/maxcount
            c += 1
            totdiv += 1
        # print(f"{idxsrc:6} to {idxdest:6} with tots {tots}, count of window {totdiv}, making {tots/totdiv:15.8f}")
        return tots/totdiv


def count_articles(articles, topic0s, tosearches):
    count = 0
    for topset in articles:
        for i in range(len(topic0s)):
            if topic0s[i] in topset[1]:
                for top in tosearches[i]:
                    if top in topset[1]:
                        count += 1
    return count



def anneal(M, T):
    count = 0
    weightbest = 0
    weightbest_div = 0.0
    for idx_T in range(len(T)):
        print(idx_T, len(T), end='\r')
        tosearch = []
        if idx_T > 0:
            # Source with left(source)
            tosearch.append(T[idx_T - 1])
        if idx_T > 1:
            # Source with left(left(source))
            tosearch.append(T[idx_T - 2])  # len(M[T[idx_T]][1].intersection(M[T[idx_T - 2]][1]))
        if idx_T < len(T) - 1:
            # Source with right(source)
            tosearch.append(T[idx_T + 1])  # len(M[T[idx_T]][1].intersection(M[T[idx_T + 1]][1]))
        if idx_T < len(T) - 2:
            # Source with right(right(source))
            tosearch.append(T[idx_T + 2])  # len(M[T[idx_T]][1].intersection(M[T[idx_T + 2]][1]))
        weightbest += count_articles(M, [T[idx_T]], [tosearch])
        weightbest_div = sum([len(x) for x in [tosearch]])
        #if idx_T > 0:
        #    # Source with left(source)
        #    weightbest += count_articles(M, T[idx_T], T[idx_T - 1])  # count_articles(M, T[idx_T]].intersection(M[T[idx_T - 1]][1]))
        #    weightbest_div += 1.0
        #if idx_T > 1:
        #    # Source with left(left(source))
        #    weightbest += count_articles(M, T[idx_T], T[idx_T - 2])  # len(M[T[idx_T]][1].intersection(M[T[idx_T - 2]][1]))
        #    weightbest_div += 1.0

        #if idx_T < len(T) - 1:
        #    # Source with right(source)
        #    weightbest += count_articles(M, T[idx_T], T[idx_T + 1])  # len(M[T[idx_T]][1].intersection(M[T[idx_T + 1]][1]))
        #    weightbest_div += 1.0

        #if idx_T < len(T) - 2:
        #    # Source with right(right(source))
        #    weightbest += count_articles(M, T[idx_T], T[idx_T + 2])  # len(M[T[idx_T]][1].intersection(M[T[idx_T + 2]][1]))
        #    weightbest_div += 1.0


    bestlayoutP = -100
    firstlayoutP = (weightbest/weightbest_div)/len(T)
    print("STARTING")
    layoutP = 0.0
    tosearch = []
    mainsearch = []
    UPPER = len(T)-1
    for i in range(ITERATIONS):

        src_idx_T = randint(0, len(T)-1)
        dest_idx_T = src_idx_T
        while dest_idx_T == src_idx_T or dest_idx_T > UPPER:
            dest_idx_T = round(gauss(src_idx_T, 4))
            #dest_idx_T = randint(0, len(T)-1)

        # print(i, bestlayoutP, src_idx_T, dest_idx_T, len(T))
        # print('\t', T[src_idx_T], T[dest_idx_T], len(M))

        # See how strong the cohesiveness of original positions are, as compared to right and left, window of 2
        weightsrc = 0
        weightsrc_div = 0.0
        tosearch.clear()
        mainsearch.clear()

        mainsearch.append(src_idx_T)
        tosearch.append([])
        if src_idx_T > 0:
            # Source with left(source)
            tosearch[-1].append(T[src_idx_T - 1])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
        if src_idx_T > 1:
            # Source with left(left(source))
            tosearch[-1].append(T[src_idx_T - 2])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T - 2]][1]))
        if src_idx_T < len(T) - 1:
            # Source with right(source)
            tosearch[-1].append(T[src_idx_T + 1])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T + 1]][1]))
        if src_idx_T < len(T) - 2:
            # Source with right(right(source))
            tosearch[-1].append(T[src_idx_T + 2])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T + 2]][1]))

        mainsearch.append(dest_idx_T)
        tosearch.append([])
        if dest_idx_T > 0:
            # Destination with left(destination)
            tosearch[-1].append(T[dest_idx_T - 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))
        if dest_idx_T > 1:
            # Destination with left(left(destination))
            tosearch[-1].append(T[dest_idx_T - 2])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T - 2]][1]))
        if dest_idx_T < len(T) - 1:
            # Destination with right(destination)
            tosearch[-1].append(T[dest_idx_T + 1])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T + 1]][1]))
        if dest_idx_T < len(T) - 2:
            # Destination with right(right(destination))
            tosearch[-1].append(T[dest_idx_T + 2])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T + 2]][1]))

        weightsrc += count_articles(M, mainsearch, tosearch)
        weightsrc_div = sum([len(x) for x in tosearch])
        """
        if src_idx_T > 0:
            # Source with left(source)
            weightsrc += count_articles(M, T[src_idx_T], T[src_idx_T - 1])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
            weightsrc_div += 1.0
        if src_idx_T > 1:
            # Source with left(left(source))
            weightsrc += count_articles(M, T[src_idx_T], T[src_idx_T - 2])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T - 2]][1]))
            weightsrc_div += 1.0
        if src_idx_T < len(T) - 1:
            # Source with right(source)
            weightsrc += count_articles(M, T[src_idx_T], T[src_idx_T + 1])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T + 1]][1]))
            weightsrc_div += 1.0
        if src_idx_T < len(T) - 2:
            # Source with right(right(source))
            weightsrc += count_articles(M, T[src_idx_T], T[src_idx_T + 2])  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T + 2]][1]))
            weightsrc_div += 1.0
        if dest_idx_T > 0:
            # Destination with left(destination)
            weightsrc += count_articles(M, T[dest_idx_T], T[dest_idx_T - 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))
            weightsrc_div += 1.0
        if dest_idx_T > 1:
            # Destination with left(left(destination))
            weightsrc += count_articles(M, T[dest_idx_T], T[dest_idx_T - 2])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T - 2]][1]))
            weightsrc_div += 1.0
        if dest_idx_T < len(T) - 1:
            # Destination with right(destination)
            weightsrc += count_articles(M, T[dest_idx_T], T[dest_idx_T + 1])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T + 1]][1]))
            weightsrc_div += 1.0
        if dest_idx_T < len(T) - 2:
            # Destination with right(right(destination))
            weightsrc += count_articles(M, T[dest_idx_T], T[dest_idx_T + 2])  #  len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T + 2]][1]))
            weightsrc_div += 1.0
        """


        mainsearch.clear()
        tosearch.clear()
        # See how strong cohesiveness of destination for both, window of 2
        weightdest = 0
        weightdest_div = 0.0
        mainsearch.append(dest_idx_T)
        tosearch.append([])
        if src_idx_T > 0:
            # Destination with left(source)
            tosearch[-1].append(T[src_idx_T - 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
        if src_idx_T > 1:
            # Destination with left(left(source))
            tosearch[-1].append(T[src_idx_T - 2])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T - 2]][1]))
        if src_idx_T < len(T) - 1:
            # Destination with right(source)
            tosearch[-1].append(T[src_idx_T + 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T + 1]][1]))
        if src_idx_T < len(T) - 2:
            # Destination with right(right(source))
            tosearch[-1].append(T[src_idx_T + 2])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T + 2]][1]))

        mainsearch.append(src_idx_T)
        tosearch.append([])
        if dest_idx_T > 0:
            # Source with left(destination)
            tosearch[-1].append(T[dest_idx_T - 1])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))
        if dest_idx_T > 1:
            # Source with left(left(destination))
            tosearch[-1].append(T[dest_idx_T - 2])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T - 2]][1]))
        if dest_idx_T < len(T) - 1:
            # Source with right(destination)
            tosearch[-1].append(T[dest_idx_T + 1])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T + 1]][1]))
        if dest_idx_T < len(T) - 2:
            # Source with right(right(destination))
            tosearch[-1].append(T[dest_idx_T + 2])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T + 2]][1]))

        weightdest += count_articles(M, mainsearch, tosearch)
        weightdest_div = sum([len(x) for x in tosearch])

        """        if src_idx_T > 0:
            # Destination with left(source)
            weightdest +=  count_articles(M, T[dest_idx_T], T[src_idx_T - 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
            weightdest_div = 1.0
        if src_idx_T > 1:
            # Destination with left(left(source))
            weightdest +=  count_articles(M, T[dest_idx_T], T[src_idx_T - 2])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T - 2]][1]))
            weightdest_div = 1.0
        if src_idx_T < len(T) - 1:
            # Destination with right(source)
            weightdest +=  count_articles(M, T[dest_idx_T], T[src_idx_T + 1])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T + 1]][1]))
            weightdest_div = 1.0
        if src_idx_T < len(T) - 2:
            # Destination with right(right(source))
            weightdest +=  count_articles(M, T[dest_idx_T], T[src_idx_T + 2])  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T + 2]][1]))
            weightdest_div = 1.0
        if dest_idx_T > 0:
            # Source with left(destination)
            weightdest +=  count_articles(M, T[src_idx_T], T[dest_idx_T - 1])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))
            weightdest_div = 1.0
        if dest_idx_T > 1:
            # Source with left(left(destination))
            weightdest +=  count_articles(M, T[src_idx_T], T[dest_idx_T - 2])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T - 2]][1]))
            weightdest_div = 1.0
        if dest_idx_T < len(T) - 1:
            # Source with right(destination)
            weightdest +=  count_articles(M, T[src_idx_T], T[dest_idx_T + 1])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T + 1]][1]))
            weightdest_div = 1.0
        if dest_idx_T < len(T) - 2:
            # Source with right(right(destination))
            weightdest +=  count_articles(M, T[src_idx_T], T[dest_idx_T + 2])  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T + 2]][1]))
            weightdest_div = 1.0
        """





        difference = (weightdest/weightdest_div - weightsrc/weightsrc_div)/len(T)
        if difference > 0 or random() < 0.1*(ITERATIONS - i)/ITERATIONS:
            T[src_idx_T], T[dest_idx_T] = T[dest_idx_T], T[src_idx_T]
            layoutP += difference
            bestlayoutP = layoutP
            count += 1
        print(f"{i:<20}{count:<5}{layoutP:20}\t{bestlayoutP:20.8f}", end='\r')

    return T, bestlayoutP, firstlayoutP



def anneal_matrix(M, T):
    #temp = len(T)
    first = T.copy()
    cost_matrix = lookup_mat(M)
    count = 0
    weightbest = 0
    weightbest_div = 0.0
    for idx_T in range(len(T)):
        print(idx_T, len(T), end='\r')
        weightbest += cost_matrix.getrange(T, idx_T, idx_T)  # count_articles(M, T[idx_T]].intersection(M[T[idx_T - 1]][1]))

    bestlayoutP = -100
    firstlayoutP = weightbest/len(T)
    print("avg shared topics per topic with window 2 : ", firstlayoutP)
    print("STARTING")
    layoutP = 0.0
    UPPER = len(T)-1
    for i in range(ITERATIONS):

        src_idx_T = randint(0, len(T)-1)
        dest_idx_T = src_idx_T
        while dest_idx_T == src_idx_T or dest_idx_T > UPPER:
            dest_idx_T = round(gauss(src_idx_T, 10))
            #dest_idx_T = randint(0, len(T)-1)

        # print(i, bestlayoutP, src_idx_T, dest_idx_T, len(T))
        # print('\t', T[src_idx_T], T[dest_idx_T], len(M))

        # See how strong the cohesiveness of original positions are, as compared to right and left, window of 2
        weightsrc = 0
        weightdest = 0

        weightsrc += cost_matrix.getrange(T, src_idx_T, src_idx_T)  # len(M[T[src_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
        weightsrc += cost_matrix.getrange( T, dest_idx_T, dest_idx_T)  # len(M[T[dest_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))
        weightdest +=  cost_matrix.getrange( T, dest_idx_T, src_idx_T)  # len(M[T[dest_idx_T]][1].intersection(M[T[src_idx_T - 1]][1]))
        weightdest +=  cost_matrix.getrange( T, src_idx_T, dest_idx_T)  # len(M[T[src_idx_T]][1].intersection(M[T[dest_idx_T - 1]][1]))

        difference = (weightdest - weightsrc)/len(T)
        if difference > 0 or random() < 100000*((ITERATIONS-i)/ITERATIONS)*abs(difference):
            T[src_idx_T], T[dest_idx_T] = T[dest_idx_T], T[src_idx_T]
            layoutP += difference
            bestlayoutP = layoutP
            count += 1
        #temp = 0.99*temp
        print(f"{i/ITERATIONS:10.8f} {i:<20}{count:<10}{layoutP:30.8f}\t{bestlayoutP:20.8f}\t{difference:30.8f}", end='\r')

    print(f"{i:<20}{count:<5}{layoutP:20}\t{bestlayoutP:20.8f}")
    weightlast = 0
    for idx_T in range(len(T)):
        print(idx_T, len(T), end='\r')
        weightlast += cost_matrix.getrange( T, idx_T, idx_T)  # count_articles(M, T[idx_T]].intersection(M[T[idx_T - 1]][1]))

    print("END avg shared topics per topic with window 2 : ", (weightbest)/len(T))
    print(f"first is {'NOT' if first!=T else ''} equal to last")

    return T, bestlayoutP, firstlayoutP




def flatten_sent(flat, loaded_mtx, source):
    prevk = 0
    prevkey = len(flat)
    base = len(flat)
    for k, v in loaded_mtx.items():
        # k == [articleNum, topicNum]
        # v == [-, neu, +]
        if k[0]+base - prevk > 0:
            prevkey = len(flat)
            prevk = k[0]+base
        if prevkey >= len(flat):
            flat.append([source, set()])
        if sum(v) > 0:
            flat[prevkey][1].add(k[1])
    """
        prevk = k[0]
        print(k, v)
        input()
        if (k[1] in flat):
            flat[k[1]] = sum(v) + flat[k[1]]
        else:
            flat[k[1]] = sum(v)
    return flat
    """
    return flat


def temp(i):
    return i


def load_matrix(path):
    all_files = {}
    sources = os.listdir(path)

    for s in sources:
        source_path = os.path.join(path, s)
        pkls = (f for f in os.listdir(source_path) if f.endswith('.' + 'pkl'))
        for p in pkls:
            file_path = os.path.join(source_path, p)
            if (not source_path in all_files):
                all_files[source_path] = []
            all_files[source_path].append(file_path)

    articles_topics = []
    for source in all_files:
        src = source.replace('matrices', '').replace('.com', '').replace('www.', '').replace('data', '').replace(os.pathsep, '')
        for file in all_files[source]:
            loaded_mtx = jsv_dictmat(file)
            flatten_sent(articles_topics, loaded_mtx, src)

    all_topics = set()
    for topics in articles_topics:
        all_topics.update(topics[1])

    return articles_topics, list(all_topics)


def run(outdir='sa_out'):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    M, topics = load_matrix(os.path.join('data', 'matrices'))
    bestlayout, bestlayoutP, firstlayoutP = anneal_matrix(M, topics)
    print("M, topics, idx2NE, bestlayout, bestlayoutP, firstlayoutP")

    with open("words2resolved.txt", encoding='utf-8') as F:
        idx2NE = {i: ' '.join(x.split(' ')[1:]) for i, x in enumerate(F.read().split('\n')[:-1])}
    with open("PossibleSA.txt", 'w', encoding='utf-8') as F:
        F.write('\n'.join([idx2NE[x] for x in bestlayout]))

    return M, topics, idx2NE, bestlayout, bestlayoutP, firstlayoutP
