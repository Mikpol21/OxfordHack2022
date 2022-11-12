from flask import Flask, request, render_template
import ingredients_scraper
import evaluate_footprint
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def my_form():
    return render_template('search_box.html', result = {})


@app.route('/', methods=['POST'])
def my_form_post():
    try:
      text = request.form['search']
      ingredients = ingredients_scraper.get_ingredients(text)
      footprint = evaluate_footprint.extract_footprint(ingredients)
      total_footprint = sum([x[0] for x in footprint])
      dict = {}
      idx = 0
      for x, y in zip(ingredients, footprint):
          dict[idx] = [x,y]
          idx += 1
      return render_template('search_box.html', result=dict, total=total_footprint)
    except:
      return render_template('search_box.html', result={}, total=0)