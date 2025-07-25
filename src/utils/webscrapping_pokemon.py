import requests
from lxml import html

res = requests.get("https://pokemondb.net/pokedex/all")

tree = html.fromstring(res.content)


pokemons = tree.xpath("//table[@id='pokedex']/tbody/tr")
requete = "INSERT INTO pokemon " \
          "(name ,pokedex_number,hp, attack, defense, spe_atk, spe_def, speed, id_pokemon_type, level, url_image) VALUES "
already_see_dex = []
for pokemon in pokemons:
    hp, attack, defense, spe_atk, spe_def, speed = pokemon.xpath(".//td[@class='cell-num']/text()")
    hp, attack, defense, spe_atk, spe_def, speed=int(hp), int(attack), int(defense), int(spe_atk), int(spe_def), int(speed)
    #name = pokemon.xpath(".//td[@class='cell-name']/a/text()")[0]
    url_image = pokemon.xpath(".//*[contains(@class, 'icon-pkmn')]")[0].attrib['data-src']
    pokedex_num = int(pokemon.xpath(".//span[contains(@class, 'infocard-cell-data')]")[0].text)
    if pokedex_num in already_see_dex:
        continue
    already_see_dex.append(pokedex_num)
    name  = url_image.split("/")[-1].split(".")[0].replace("-", " ").title()

    physical_sweeper = (attack + speed) / 2
    special_sweeper = (spe_atk + speed) / 2
    wall = (hp + defense + spe_def) / 3
    physical_tank = (attack + defense) / 2
    special_tank = (spe_atk + spe_def) / 2

    if special_sweeper == max(physical_sweeper, special_sweeper, wall, physical_tank, special_tank):
        type = 1
    elif wall == max(physical_sweeper, special_sweeper, wall, physical_tank, special_tank):
        type = 2
    elif physical_sweeper == max(physical_sweeper, special_sweeper, wall, physical_tank, special_tank):
        type = 3
    elif special_tank == max(physical_sweeper, special_sweeper, wall, physical_tank, special_tank):
        type = 4
    elif physical_tank == max(physical_sweeper, special_sweeper, wall, physical_tank, special_tank):
        type = 5

    requete+=f"\n('{name}',{pokedex_num} ,{hp}, {attack}, {defense}, {spe_atk}, {spe_def}, {speed}" \
             f", {type}, 100, '{url_image}'),"


with open("list_pokemon.txt", mode='w+', encoding='utf8') as f :
    f.write(requete)
