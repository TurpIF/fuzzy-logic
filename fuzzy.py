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


if __name__ == '__main__':
    # HUMIDITY x TEMPERATURE
    hum_sets = {'Sec' : (0, 40), 'Humide': (60, 70), 'Trempé': (80, 100)}
    hum_fuzzy = Fuzzyfier(hum_sets)


    temp_sets = {'Froide' : (0, 5), 'Douce': (13, 13), 'Normale': (18, 22), 'Chaude': (26, 30),
                  'Caniculaire': (38, 45)}
    temp_fuzzy = Fuzzyfier(temp_sets)


    spray_rules = {('Sec', 'Froide') : 'Courte', ('Sec', 'Douce') : 'Moyenne', ('Sec', 'Normale') : 'Moyenne',
                   ('Sec', 'Chaude') : 'Longue', ('Sec', 'Caniculaire') : 'Longue', ('Humide', 'Douce') : 'Courte',
                   ('Humide', 'Normale') : 'Moyenne', ('Humide', 'Chaude') : 'Moyenne',
                   ('Humide', 'Caniculaire'): 'Longue', ('Trempé', 'Caniculaire'): 'Courte'}

    spray_controler = Controler(hum_fuzzy, temp_fuzzy, spray_rules)

    assert spray_controler.fuzzy_values(65, 33) == {'Moyenne': 0.625, 'Longue': 0.375}
    assert spray_controler.fuzzy_values(50, 6) == {'Courte': 0.5, 'Moyenne': 0.125}


    # TH_SPRAY x NAPPE
    spray_sets = {'Nulle' : (0, 0), 'Courte' : (0, 5), 'Moyenne': (10, 10), 'Longue': (30, 30)}
    spray_fuzzy = Fuzzyfier(spray_sets)

    nappe_sets = {'Insuffisant' : (0, 1), 'Faible': (1.5, 1.5), 'Suffisant': (2, 10)}
    nappe_fuzzy = Fuzzyfier(nappe_sets)


    real_spray_rules = {('Courte', 'Suffisant'): 'Courte', ('Moyenne', 'Faible'): 'Courte',
                       ('Moyenne', 'Suffisant') : 'Moyenne', ('Longue', 'Faible') : 'Moyenne',
                       ('Longue', 'Suffisant') : 'Longue'}

    real_spray_controler = Controler(spray_fuzzy, nappe_fuzzy, real_spray_rules)

    # REAL_SPRAY x HUM_SENSIBILITY
    real_spray_sets = spray_sets
    real_spray_fuzzy = Fuzzyfier(real_spray_sets)


    hum_sens_sets = {'Marine' : (0, 10), 'Urbaine': (50, 50), 'Désertique': (90, 100)}
    hum_sens_fuzzy = Fuzzyfier(hum_sens_sets)

    att_spray_rules = {('Marine', 'Nulle') : 'Nulle', ('Marine', 'Courte'): 'Courte',
                       ('Marine', 'Moyenne'): 'Moyenne', ('Marine', 'Longue'): 'Longue',

                       ('Urbaine', 'Nulle') : 'Nulle', ('Urbaine', 'Courte'): 'Nulle',
                       ('Urbaine', 'Moyenne'): 'Courte', ('Urbaine', 'Longue'): 'Moyenne',

                       ('Désertique', 'Nulle') : 'Nulle', ('Désertique', 'Courte'): 'Nulle',
                       ('Désertique', 'Moyenne'): 'Nulle', ('Désertique', 'Longue'): 'Courte'}

    att_spray_controler = Controler(hum_sens_fuzzy, real_spray_fuzzy, att_spray_rules)

    att_spray_sets = spray_sets
    att_spray_fuzzy = Fuzzyfier(att_spray_sets)

    def calculate_real_spray(nappe, humidity, temperature):
        fuzzy_s = spray_controler.fuzzy_values(humidity, temperature)
        s = spray_fuzzy.defuzzyfy(fuzzy_s)

        fuzzy_real_spray = real_spray_controler.fuzzy_values(s, nappe)

        return real_spray_fuzzy.defuzzyfy(fuzzy_real_spray)

    # print calculate_real_spray(nappe=3, humidity=81, temperature=37)
    assert calculate_real_spray(nappe=10, humidity=100, temperature=0) == 0
    # print calculate_real_spray(nappe=1.4, humidity=50, temperature=6)

    def calculate_att_spray(nappe, humidity, temperature, sensibility):
        real_spray = calculate_real_spray(nappe, humidity, temperature)

        att_spray = att_spray_controler.fuzzy_values(sensibility, real_spray)

        return att_spray_fuzzy.defuzzyfy(att_spray)

    def compare_spray(nappe, humidity, temperature):
        spray = calculate_real_spray(nappe, humidity, temperature)
        print '* Original spray: {}'.format(spray)
        print ''

        for sensibility in [10, 20, 30, 50, 100]:

            print '# Sensibility = {}'.format(sensibility)

            att_spray = calculate_att_spray(nappe, humidity, temperature, sensibility)
            print '  - Attenuated spray: {}'.format(att_spray)


    nappe, humidity, temperature = (1.75, 65, 33)

    compare_spray(nappe, humidity, temperature)

