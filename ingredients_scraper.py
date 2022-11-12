from bs4 import BeautifulSoup
import requests


def get_bbc_good_food_URL(text):
    page = requests.get('https://www.bbcgoodfood.com/search?q=' + text.replace(' ', '+'))
    soup = BeautifulSoup(page.content, 'html.parser')
    thumbnail = soup.find_all('div', class_='standard-card-new__thumbnail')
    #print(thumbnail[0].find('a')['href'])
    return 'https://www.bbcgoodfood.com' + thumbnail[0].find('a')['href']

def extract_ingredients_BBC_good_food(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find_all('li', class_='pb-xxs pt-xxs list-item list-item--separator')

def prettify_ingredients(ingredients_list):
    ingredients = []
    for ingredient in ingredients_list:
        ingredients.append(ingredient.text)
    return ingredients

def get_ingredients(dish):
    URL = get_bbc_good_food_URL(dish)
    # print(URL)
    ingredients_list = extract_ingredients_BBC_good_food(URL)
    return prettify_ingredients(ingredients_list)

print(get_ingredients("chicken katsu"))

"""
Units:
    ml
    g
    quantity (1 , 1 ½)
    tsp
    tbsp
    2 x 400g
    fl oz
    kg
    litre (or l)
    
"""