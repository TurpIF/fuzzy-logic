#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fuzzy import Fuzzyfier, Controler

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

