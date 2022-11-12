from gensim.test.utils import common_texts
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import gensim
import numpy as np
import gensim.downloader
import re
import pandas as pd
from copy import deepcopy
from pandas import DataFrame as df


# ====================================================
# 					LOAD DATA
# ====================================================


# Show all available models in gensim-data
glove_vectors = gensim.downloader.load('glove-wiki-gigaword-50')


food_data = pd.read_csv('fooddata.csv')
food_data = food_data.dropna()

food_dict = {}
for name, serving, per100 in zip(food_data['Name'], food_data['Suggested_Serving'], food_data['per100g']):
	food_dict[name] = (serving, per100)


# ====================================================
# 					FUNCTIONS
# ====================================================

def preprocess(line):
	res = line.lower()
	res = res.replace('(', '').replace(')', '').replace('/', ' ').replace('-', ' ').replace('\'', '').replace('\"', '').replace('?', '').replace('!', '').replace(',', '').replace(';', '').replace(':', '')
	res = res.replace(' one ', ' 1 ').replace(' two ', ' 2 ').replace(' three ', ' 3 ').replace(' four ', ' 4 ').replace(' five ', ' 5 ').replace(' six ', ' 6 ').replace(' seven ', ' 7 ').replace(' eight ', ' 8 ').replace(' nine ', ' 9 ').replace(' ten ', ' 10 ')
	res = " ".join(re.split(',| |\|/', res))

	mults = re.findall(r"[0-9]+[\s]*[x,\\,+][\s]*[0-9]+", res)
	for m in mults:
		res = res.replace(m, str(eval(m.replace('x', '*'))))
	return res


def extract_amount(line):
	grams = re.findall(r"[0-9]+[\s]*[mk]*g ", line)
	litres = re.findall(r"[0-9]+[\s]*[m]*l ", line)
	litres = litres + re.findall(r"[0-9]+[\s]*[m]*litre", line)
	ounces = re.findall(r"[0-9]+[\s]*oz[s]* ", line)
	fl_ounces = re.findall(r"[0-9]+[\s]*fl oz[s]* ", line)
	pounds = re.findall(r"[0-9]+[\s]*lb[s]* ", line)
	teaspoons = re.findall(r"[0-9]+[\s]*[tT]sp[s]* ", line)
	tablespoons = re.findall(r"[0-9]+[\s]*tbsp[s]* ", line)
	cups = re.findall(r"[0-9]+[\s]*[cC]up[s]* ", line)
	pints = re.findall(r"[0-9]+[\s]*[pP]int[s]* ", line)
	quarts = re.findall(r"[0-9]+[\s]*[qQ]uart[s]* ", line)
	gallons = re.findall(r"[0-9]+[\s]*[gG]allon[s]* ", line)
	pieces = re.findall(r"[0-9]+[\s]*[pP]iece[s]* ", line)
	portions = re.findall(r"[0-9]+[\s]*[pP]ortion[s]* ", line)
	slice = re.findall(r"[0-9]+[\s]*[sS]lice[s]* ", line)

	numbers = re.findall(r"[0-9]+[\s]*", line)
	numbers = [item+"portion" for item in numbers]

	amounts = grams + litres + ounces + fl_ounces + pounds + teaspoons + tablespoons + cups + pints + quarts + gallons + pieces + portions
	amounts = numbers if amounts == [] else amounts
	if amounts == []: amounts = ['1 portion ']

	amounts = amounts[0].replace(' ', '')
	amounts = amounts[:-1] if amounts[-1]=='s' else amounts

	return amounts

def unify_amount(amount, product):
	amount = amount.replace('kg', '*1000')
	amount = amount.replace('mg', '*0.1')
	amount = amount.replace('ml', '')
	amount = amount.replace('litre', '*1000')
	amount = amount.replace('floz', '*28.3495')
	amount = amount.replace('oz', '*28.3495')
	amount = amount.replace('lb', '*453.592')
	amount = amount.replace('tsp', '*4.92892')
	amount = amount.replace('tbsp', '*14.7868')
	amount = amount.replace('cup', '*236.588')
	amount = amount.replace('pint', '*473.176')
	amount = amount.replace('quart', '*946.353')
	amount = amount.replace('gallon', '*3785.41')
	amount = amount.replace('piece', 'portion')
	amount = amount.replace('slice', 'portion')
	amount = amount.replace('g', '')
	amount = amount.replace('l', '*1000')

	# ! TODO: replace portion with sth smart
	portion_size = str(food_dict[product][0])
	amount = amount.replace('portion', '*'+portion_size)
	
	return eval(amount)


def extract_product(line):
	keywords = re.sub(r'\W+', ' ', line).split()
	applicable = []
	for key in food_dict.keys():
		if ' ' in key:
			if line.find(key) != -1:
				applicable.append(key)
		else:
			if key in keywords or key+'s' in keywords:
				applicable.append(key)
			if key[-1]=='s' and key[:-1] in keywords:
				applicable.append(key)

	max_sim  = 0
	best_ingredient = ''

	if applicable == []:
		for key in food_dict.keys():
			similarity = 0
			if key in glove_vectors:
				similarity = np.max(glove_vectors.cosine_similarities(glove_vectors[key], [glove_vectors[word] if word in glove_vectors else glove_vectors['troll'] for word in keywords]))
			if similarity > max_sim:
				max_sim = similarity
				best_ingredient = key
		return best_ingredient
	return max(applicable, key=len)


def extract_footprint(ingredients):
	
	new_ingredients = deepcopy(ingredients)
	for i in range(len(new_ingredients)):
		new_ingredients[i] = preprocess(new_ingredients[i])

	result = []

	for i in range(len(new_ingredients)):
		product = extract_product(new_ingredients[i])
		amount = (unify_amount(extract_amount(new_ingredients[i]), product))
		
		result.append((round(amount*food_dict[product][1]/100), amount, food_dict[product][1]))

	return result


# ====================================================
# 						EXAMPLES
# ====================================================


ingr_ex_1 = ['a good beef fillet (preferably Aberdeen Angus) of around 1kg/2lb 4oz','3 tbsp olive oil','250g/9oz chestnut mushroom, include some wild ones if you like','50g/2oz butter','1 large sprig fresh thyme','100ml/3.5 fl oz dry white wine','2 x 6 slices prosciutto','1+1kg/1lb 2oz pack puff pastry, thawed if frozen','a little flour, for dusting','2 egg yolks beaten with 1 tsp water']
ingr_ex_2 = ['1/2 cup (125 mL) unsalted butter, softened','1/2 cup (125 mL) granulated sugar','1/2 cup (125 mL) packed brown sugar','1 large egg','1 tsp (5 mL) vanilla extract','1 1/2 cups (375 mL) all-purpose flour','1/2 tsp (2 mL) baking soda','1/2 tsp (2 mL) salt','1 cup (250 mL) old-fashioned rolled oats','1 cup (250 mL) semisweet chocolate chips','1 cup (250 mL) white chocolate chips','1 cup (250 mL) dried cranberries','1 cup (250 mL) chopped pecans']
ingr_ex_3 = ['650ml milk', '40g plain flour', '40g butter', '2 tsp Dijon mustard', '150g mature  cheddar, grated', '180g frozen peas', 'handful of  parsley, chopped', '300g macaroni', '300g fish pie mix (smoked fish, white fish and salmon)', 'green salad, to serve (optional)']
ingr_ex_4 = ['1 tsp plain flour', '1 tsp mustard powder', '950g beef top rump joint (see tip below)', '1 onion, cut into 8 wedges', '500g carrots, halved lengthways', '1 tbsp plain flour', '250ml beef stock']