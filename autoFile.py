#! /usr/bin/python

import sys
import os
import subprocess

args = sys.argv


if len(args) > 1:
	path = args[1]
else:
	path = '.'

# Separate files for cake mix and icing

text1 = '''
def makeBatter(flour, sugar, eggs):

	flour.append(sugar)

	flour.append(eggs)

	return flour


def addChocolate(cake, chocolate):

	cake.append(chocolate)

	return cake


def addIcing(cake, icing):

	cake.append(icing)

	return cake
'''

text2 = '''
def preHeat(oven):

	oven.heat(185)

	return oven


def timer(oven, minutes):

	oven.timer(minutes)

	oven.timer.start()


def bake(oven, cake):

	oven.append(cake)

	timer(oven, 35)

'''


os.chdir(path)

subprocess.call(['subl', '-an', path])

files = ['cake.py', 'baking.py']
texts = [text1, text2]

for i,file in enumerate(files):

	with open(file, 'w') as f:
		f.write(texts[i])

	subprocess.call(['subl', file])


