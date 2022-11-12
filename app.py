from flask import Flask, request, render_template
import ingredients_scraper
import evaluate_footprint

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def my_form():
    return render_template('search_box.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['search']
    ingredients = ingredients_scraper.get_ingredients(text)
    footprint = evaluate_footprint.extract_footprint(ingredients)
    return list(zip(ingredients, footprint))

"""
<form method="POST">
  <input name="text" />
  <input type="submit" />
</form>
"""