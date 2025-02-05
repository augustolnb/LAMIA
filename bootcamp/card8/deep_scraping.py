from bs4 import BeautifulSoup
import requests
import pandas as pd

def find_pokemons():
    # URL da página da Wikipedia Pokémon
    url = 'https://pokemon.fandom.com/wiki/List_of_Pok%C3%A9mon'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')

    # Encontrar todas as tabelas da Pokédex
    pokedex_tables = soup.find_all('table', class_='wikitable')

    # Lista para armazenar os dados dos Pokémon
    pokemon_list = []

    # Iterar sobre cada tabela (geração)
    for table in pokedex_tables:
        rows = table.find_all('tr')

        # Iterar sobre cada linha da tabela (exceto o cabeçalho)
        for row in rows[1:]:
            columns = row.find_all('td')

            # Verificar se a linha contém dados válidos
            if len(columns) >= 3:
                # Extrair o número na Pokédex
                pokedex_number = columns[0].text.strip()

                # Extrair o nome do Pokémon
                name_tag = columns[1].find('a', href=True, title=True)
                name = name_tag['title'] if name_tag else 'Desconhecido'

                # Extrair os tipos do Pokémon
                type_tags = columns[2].find_all('span', class_=['t-type', 't-type2'])
                types = list(set(tag.text.strip() for tag in type_tags))

                # Adicionar os dados à lista
                pokemon_list.append({
                    "Número": pokedex_number,
                    "Nome": name,
                    "Tipos": types
                })

    # Salvar os dados em um arquivo CSV
    df = pd.DataFrame(pokemon_list)
    #df.to_csv('pokedex.csv', index=False)
    #print("Dados salvos em 'pokedex.csv'.")
    print(df)
    
if __name__ == "__main__":
    find_pokemons()