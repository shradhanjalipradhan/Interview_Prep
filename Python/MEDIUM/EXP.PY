import requests
from bs4 import BeautifulSoup

def decode_secret_message(url):
  #fetched published Doc HTML
  response = requests.get(url)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, "html.parser")
  points = []

  for row in soup.find_all('tr')[1:]:
    cells = row.find_all(['td','th'])
    if len(cells) != 3:
      continue

    try:
      x =int(cells[0].get_text(strip = True))
      char = cells[1].get_text(strip=True)
      y =int(cells[2].get_text(strip = True))
      points.append((x,y,char))

    except ValueError:
      continue

  if not points:
    print('No valid data found')
    return

  max_x = max(x for x,y,char in points)
  max_y = max(y for x,y,char in points)

  grid = [['' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

  for x, y, char in points:
    grid[y][x] = char

  for row in grid:
    print(''.join(row))

decode_secret_message('https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub')