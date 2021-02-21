import os


print(os.path.dirname(os.path.abspath(__file__)))
print(os.path.abspath(__file__))

def return_files(listofdiritems):
    toret = []
    for fullpath in listofdiritems:
        if os.path.isfile(fullpath):
            toret.append( fullpath )
        if os.path.isdir(fullpath):
            if 'venv' in fullpath or '__' in fullpath:
                continue
            nextitems = os.listdir(fullpath)
            nextitems = [os.path.join(fullpath, x) for x in nextitems]
            toret +=  return_files(nextitems)
    return toret


def find_imp(toscan):
    toret = []
    for line in open(toscan, encoding='utf-8'):
        if 'import' not in line:
            continue
        toret.append(line)
    return toret


def all_imp_files(my_files):
    toret = []
    for f in my_files:
        if not f.endswith('.py'):
            continue
        toret.append((f, find_imp(f)))
    return toret

def reassemble(statement):
    if 'import ' not in statement:
        return ''
    start, end = statement.split('import ')
    if 'from ' in start:
        start = start.split('from ')[1]
    if 'as ' in end:
        end = end.split('as ')[0]
    return f"{start}{end}".replace(' ', '.')

def process_data(data):
    toret = []
    for script, listofimps in data:
        for imp in listofimps:
            toret.append((imp, script))
    return toret

def graph(data):
    import networkx as nx
    from matplotlib import pyplot as plt
    plt.tight_layout()
    g = nx.DiGraph()
    g.add_edges_from(data)
    nx.draw_networkx(g, arrows=True)
    plt.savefig("g.jpg", format="jpg")
    plt.clf()
    return data

def run():
    from jsvnews.definitions import ROOT_DIR
    my_files = return_files(os.listdir(ROOT_DIR))
    all_imports = all_imp_files(my_files)
    all_imports = [(x,[reassemble(y.strip().split('#')[0]) for y in l]) for x, l in all_imports if l]
    #graph(process_data(all_imports))
    return process_data(all_imports)