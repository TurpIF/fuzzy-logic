#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter

class Fuzzyfier(object):

    def __init__(self, fuzzy_dict):
        self.fuzzy_dict = fuzzy_dict
        self.fuzzy_sets = sorted(fuzzy_dict.iteritems(), key=lambda t : t[1][1])

    @property
    def min_value(self):
        return self.fuzzy_sets[0][1][0]

    @property
    def max_value(self):
        return self.fuzzy_sets[-1][1][1]

    def fuzzy_values(self, value):
        if value < self.min_value or value > self.max_value:
            raise ValueError("Value out of known ranges")

        for i, (c_name, (c_min, c_max)) in enumerate(self.fuzzy_sets):
            if c_min <= value <= c_max:
                return {c_name: 1.0}

            n_name, (n_min, n_max) = self.fuzzy_sets[i + 1]

            if c_max < value < n_min:
                res = dict()
                res[n_name] = float(value - c_max) / (n_min - c_max)
                res[c_name] = 1.0 - res[n_name]
                return res

    def defuzzyfy(self, fuzzy_values, interval=1):
        fuzzy_values = Counter(fuzzy_values)

        perc_sum = 0.0
        weighted_sum = 0.0

        for v in xrange(self.min_value, self.max_value + 1, interval):
            f_v = self.fuzzy_values(v)
            f_v = {name : min(perc, fuzzy_values[name]) for name, perc in f_v.iteritems()}

            max_v = max(f_v.values())

            perc_sum += max_v
            weighted_sum += max_v * v

        if perc_sum == 0:
            return 0

        return weighted_sum / perc_sum

class Controler(object):
    def __init__(self, fuzzy_a, fuzzy_b, rules):
        self.fuzzy_a = fuzzy_a
        self.fuzzy_b = fuzzy_b
        self.rules = rules

    def fuzzy_values(self, val_a, val_b):
        f_a = self.fuzzy_a.fuzzy_values(val_a)
        f_b = self.fuzzy_b.fuzzy_values(val_b)

        res = Counter()
        for a_name, a_value in f_a.iteritems():
            for b_name, b_value in f_b.iteritems():
                if not (a_name, b_name) in self.rules:
                    continue

                r_name = self.rules[(a_name, b_name)]

                res[r_name] = max(res[r_name], min(a_value, b_value))

        return res
