import requests
from lxml import html, etree

res = requests.get("https://pokemondb.net/move/all")

tree = html.fromstring(res.content)

attacks = tree.xpath("//table[@id='moves']/tbody/tr")
map_type_db = {
    "Special": 3,
    "Physical": 2,
    "Status": 4,
}
print(attacks)
requete = "INSERT INTO attack(id_attack_type, power,accuracy, element, attack_name_or_id, attack_description) VALUES"
for attack in attacks:
    if not attack.xpath(".//td/img") or not attack.xpath(".//td[@class='cell-long-text']/text()"):
        continue
    name, elem = attack.xpath(".//td/a/text()")
    name = name.replace("'", "''")
    type = map_type_db[attack.xpath(".//td/img")[0].attrib['alt']]
    numerical_value = attack.xpath(".//td[@class='cell-num']/text()")
    power = int(numerical_value[0]) if numerical_value[0] != '—' else 0
    accuracy = int(numerical_value[1]) if numerical_value[1] != '—' else 0
    description = attack.xpath(".//td[@class='cell-long-text']/text()")[0].replace("'", "''")

    requete+= f"\n({type},{power}, {accuracy}, '{elem}', '{name}','{description}'),"

print(requete)
