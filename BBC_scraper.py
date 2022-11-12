from bs4 import BeautifulSoup
import requests

URL = "https://www.bbcgoodfood.com/recipes/beef-wellington"
page = requests.get(URL)



soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())