from bs4 import BeautifulSoup
import requests
import time
import pandas as pd

def find_pokemons():

    print('#####################################')
    print('############## POKEDEX ##############')
    print('#####################################')
    print('\nNome do pokemon')
    op = input('> ')

    html_text = requests.get('https://pokemon.fandom.com/wiki/List_of_Pok%C3%A9mon').text
    soup = BeautifulSoup(html_text, 'lxml')
    pokedex = soup.find_all('table', class_='wikitable')

    pokemon_list = []

    for index, generation in enumerate(pokedex):
        #if index == 1:
        #    break

        rows = generation.find_all('tr')
        for row in rows[1:]:
            columns = row.find_all('td')

            pokedex_number = columns[0].text.strip()

            name_tag = row.find('a', href=True, title=True)
            name = name_tag['title'] if name_tag else 'Desconhecido'

            type_tags = row.find_all('span', class_=['t-type', 't-type2'])
            types = list(set(tag.text.strip() for tag in type_tags))

            pokemon_list.append({
                "Numero": pokedex_number,
                "Nome": name,
                "Tipos": types
            })

    for pokemon in pokemon_list:
        if op == pokemon['Nome'].lower():
            print(f"Pokemon encontrado:")
            print(f"Nº na pokedex: {pokemon['Numero']}")
            print(f"Nome: {pokemon['Nome']}")
            print(f"Tipo: {pokemon['Tipos']}")

    df = pd.DataFrame(pokemon_list)
    df.to_csv('pokedex.csv', index=False)
    print("Dados salvos em 'pokedex.csv'.")
    print(df.head())

if __name__ == "__main__":
    find_pokemons()