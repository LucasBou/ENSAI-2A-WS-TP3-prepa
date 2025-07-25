import requests
from lxml import html, etree

# création du mapping nom attaque -> id
attacks_all = requests.get("http://127.0.0.1:80/attack?limit=9999").json()["results"]
dict_attack = {}
for attack in attacks_all:
    dict_attack[attack["name"]] = attack["id"]

# création du mapping nom pokemon -> id
pokemons_all = requests.get("http://127.0.0.1:80/pokemon?limit=9999").json()["results"]
dict_pokemon = {}
for pokemon in pokemons_all:
    dict_pokemon[pokemon["name"]] = pokemon["id"]

print(dict_pokemon)

res = requests.get("https://pokemondb.net/pokedex/all")
tree = html.fromstring(res.content)
pokemons = tree.xpath("//a[@class='ent-name']")
pokemons = tree.xpath("//table[@id='pokedex']/tbody/tr")
request = "INSERT INTO pokemon_attack(id_pokemon,id_attack, level) VALUES "
last_pokedex= None
for pokemon in pokemons:
    url_pokemon = pokemon.xpath(".//a[@class='ent-name']")[0].attrib["href"]
    pokemon_name = url_pokemon.split("/")[-1].title()
    id_pokemon = dict_pokemon.get(pokemon_name)

    print(url_pokemon)
    pokedex_num = int(pokemon.xpath(".//span[contains(@class, 'infocard-cell-data')]")[0].text)

    pokemon_file = requests.get(f"https://pokemondb.net{url_pokemon}")
    tree = html.fromstring(pokemon_file.content)
    attacks = tree.xpath('//div[@id="tab-moves-18"]//h3[text()="Moves learnt by level up"][1]/following-sibling::div[1]/table/tbody/tr')
    # print(etree.tostring(tree.xpath('//h3[text()="Moves learnt by level up"]/following-sibling::div/table/tbody/tr')))
    if last_pokedex is None or last_pokedex != pokedex_num:
        atk_list = []
        for attack in attacks:
            attack_name = attack.xpath('.//td[@class="cell-name"]/a/text()')[0]
            level = attack.xpath('.//td[@class="cell-num"]')[0].text
            id_att = dict_attack.get(attack_name)
            if atk_list is None or id_att not in atk_list and (id_att and id_pokemon and level):
                request += f"\n({pokedex_num}, {id_att}, {level}),"
            atk_list.append(id_att)
    last_pokedex = pokedex_num

with open("out.txt", mode='w+', encoding='utf8') as f :
    f.write(request)
