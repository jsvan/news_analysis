class jsv_dictmat:
    def __init__(self, N=dict()):
        """
        :param N: can be either a
                string -- open from path to pickle file
                jsv_dictmat -- copies the dictmat into this
                dict -- converts dict to jsv_dictmat
        """
        self.X, self.Y = 0, 0
        self.M = dict()
        self.top2idx = dict()
        if isinstance(N, str):
            self.load(N)
        else:
            self.update(N)

    def __add__(self, N):
        """
        Updates in place, so changes the first matrix in string
        of m0 + m1 + m2 + m3 + m4, m0 will be altered to hold
        the final value.
        If adding the same matrix to itself (m+m+m+m)
        values will double each time, as the matrix to add is
        being updated along with the m0 matrix, because it _is_
        the m0 matrix."""
        raise Exception("Dont add matrices!!!!!")

    def __repr__(self):
        s = f"<{self.X}x{self.Y} sparse matrix with {len(self.M)} items in Dictionary format>"
        return s

    def __len__(self):
        print("LENGTH!!")
        return self.Y

    def __str__(self):
        ret = []
        for k, v in self.items():
            ret.append(f"  {k.__str__()}\t{v.__str__()}")
        return '\n'.join(ret)

    def __getitem__(self, k):
        return self.M[k[0], k[1]]

    def __setitem__(self, k, v):
        if len(k) != 2:
            raise Exception(f"Key must be of form (x,y), received {k}.")
        if len(v) != 3:
            raise Exception(f"Value must be of form (neg,neu,pos), received {v}.")
        self.M[k] = v
        self._update_dim_(k)

    def _update_dim_(self, k):
        if k[0] >= self.X:
            self.X = k[0] + 1
        if k[1] >= self.Y:
            self.Y = k[1] + 1

    def __truediv__(self, other):
        toret = {}
        for k, v in self.items():
            toret[k] = [v[0]/other, v[1]/other, v[2]/other]
        return jsv_dictmat(toret)


    def add_triple(self, m, n):
        return [m[0] + n[0],
                m[1] + n[1],
                m[2] + n[2]]

    def to_avg(self, v, pad=0):
        return (-1*v[0] + v[2]) /  max(sum(v), pad)

    def to_avg_scipy(self, strongopinions=0):
        #print("self.X articles is ", self.X)
        """
        :return: a single scipy matrix of the average sentiment from [-1, 1]
        """
        from scipy.sparse import dok_matrix
        ret = dok_matrix((self.X, self.Y))
        #num_opinions = {x[0]:0 for x in self.keys()}
        #for k, v in self.items():
        #    num_opinions[k[0]] += sum(v)
        #print('ORIGINAL\n', self)
        for k, v in self.items():
            #total = max(sum(v), 5)
            if sum(v) < strongopinions:
                continue
            ret[k] = self.to_avg(v, pad=10)  #  num_opinions[k[0]]  # num_opinions  # total
        return ret

    def collapse_into_day_vector(self):
        """
        Combines all mentions from all articles over that (day) matrix into as if it was a single article written that day.
        :return:
        """
        toadd = {}
        keys = list(self.keys())
        for k in keys:
            v = self.M.pop(k)
            old = (0,0,0)
            if (0, k[1]) in toadd:
                old = toadd[0, k[1]]
            toadd[0, k[1]] = self.add_triple(v, old)
        self.update(toadd)
        self.X = 1
        return self

    def to_scipy(self):
        """
        :return: 3 scipy dok_matrix's, one for each sentiment count.
        """
        from scipy.sparse import dok_matrix
        ret = {'neg':dok_matrix((self.X, self.Y)),
               'neu':dok_matrix((self.X, self.Y)),
               'pos':dok_matrix((self.X, self.Y))}
        for k, v in self.items():
            ret['neg'][k] = v[0]
            ret['neu'][k] = v[1]
            ret['pos'][k] = v[2]
        return ret


    def items(self):
        for i in self.M.items():
            yield(i)

    def keys(self):
        for i in self.M.keys():
            yield(i)

    def values(self):
        for i in self.M.values():
            yield(i)

    def update(self, N, appendmode=False):
        if not (isinstance(N, jsv_dictmat) or isinstance(N, dict)):
            raise Exception(f"Trying to add type {type(N)} to matrix, must be type matrix.")
        for k, n in N.items():
            if appendmode:
                k = (k[0] + self.X ,k[1])
            if not (type(k[0]) == type(k[1]) == int):
                raise TypeError(f"{k} requires 2 ints")
            if k[0] < 0 or k[1] < 0:
                raise IndexError(f"Requires x, y values > 0. You submitted x:{k[0]}, y:{k[1]}")
            self._update_dim_(k)
            # make sure k not < 0, 0
            # make sure k tuple
            # too slow to check
            if k in self.M:
                m = self.M[k]
                self.M[k] = self.add_triple(m, n)

            else:
                self.M[k] = n
        return self

    """def load_top2idx(self):
        import os
        with open(os.path.join('..', 'main', 'words2resolved.txt')) as F:
            # {"Adams_apple":0, "Avery_Kanel":1, etc.}
            self.top2idx = {x.split(' ')[0]: i for i, x in enumerate(F.read().split('\n'))}
    """

    def load(self, path):
        import pickle
        with open(path, 'rb') as F:
            self.update(pickle.load(F))

    """def get_path(self, p):
        ""
        Ensures existence of and returns publisher's folder for today
        :param p: path to publisher's folder
        :return: path to publisher/today's_date/
        ""
        from datetime import date
        from os.path import join as pj
        from os.path import isdir
        from os import system
        if not isdir(p):
            system(f"mkdir {p}")
        return path
        """

    def save(self, path):
        import pickle
        with open(path, 'wb') as F:
            pickle.dump(self.M, F)

    def from_model_output(self, article):
        """
        :param article: a dictionary of {"Named_entity":[15,20,8], etc. (ie [neg, neu, pos])}
        :return:
        """
        x = self.X
        toupdate = dict()
        for y, v in article.items():
            # y = self.top2idx[n_e]
            toupdate[x,y] = v
        self.update(toupdate)

    def print_path_info(self):
        """
        debugging thing to figure out where the heck this thinks it is.
        :return:
        """
        import os
        print("sparse matrix currdir")
        print('pwd')
        os.system('pwd')
        print('ls')
        os.system("ls ./")

    def print_readable(self, idx2NE):
        ret = []
        for k, v in self.items():

            ret.append(f"  [{k[0]:>2}, {idx2NE[k[1]]+']':<30}{v.__str__()}")
        for i in ret:
            print(i)