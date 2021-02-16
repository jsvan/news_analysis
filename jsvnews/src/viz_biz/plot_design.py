import matplotlib.colors as mcolors

class mark:
    def __init__(self):
        self.Ms = ['.',',','o','v','^','1','2','3','4','s','p','P','*','+','x','X','d','_']
        self.Cs = list(mcolors.BASE_COLORS.keys())[:-1] + list(mcolors.TABLEAU_COLORS.keys())

    def get(self, i):
        return self.color(i), self.marker(i)

    def color(self, i):
        return self.Cs[i%len(self.Cs)]

    def marker(self, i):
        return self.Ms[i%len(self.Ms)]

    def colors(self, a):
        return [self.color(x) for x in a]

    def markers(self, a):
        return [self.marker(x) for x in a]