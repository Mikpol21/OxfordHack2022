from flask import Flask, request, render_template
import ingredients_scraper
import evaluate_footprint
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def my_form():
    return render_template('search_box.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['search']
    ingredients = ingredients_scraper.get_ingredients(text)
    footprint = evaluate_footprint.extract_footprint(ingredients)
    
    dict = {}
    for x, y in zip(ingredients, footprint):
        dict[x] = y
    print(dict)
    return render_template('search_box.html', result=dict)