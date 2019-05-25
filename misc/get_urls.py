from bs4 import BeautifulSoup
import sys

names = []

for filename in sys.argv[1:]:
    with open(filename, "r") as f:
        html_text = f.read()
        soup = BeautifulSoup(html_text, 'html.parser')


    for item in soup.select('div.cell-padding'):
        name = item.select('a')[0].text
        names.append(name)

print("\n".join(names))
