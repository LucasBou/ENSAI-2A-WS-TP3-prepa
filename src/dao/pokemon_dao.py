from exception.resource_already_exist_exception import ResourceAlreadyExistException
import psycopg2
from dao.attack_dao import AttackDao
from models.statistics import Statistics
from models.pokemon_model import PokemonModelShort, PokemonModelFull
from typing import Any, List, Optional

from dao.abstract_dao import AbstractDao
from dao.connection_manager import ConnectionManager


class PokemonDao(AbstractDao):
    def find_all(self, type_id: Optional[int] = None, type_name: Optional[str] = None
                 , limit: int = 100, offset: int = 0) -> List[PokemonModelShort]:
        request = f"SELECT name,pokemon_type_name, id_pokemon, url_image " \
                  "\nFROM pokemon JOIN pokemon_type type ON pokemon.id_pokemon_type=type.id_type_pokemon"

        if type_id is not None:
            request += "\nWHERE id_type_pokemon=%(type_id)s"
        elif type_name is not None:
            request += "\nWHERE pokemon_type_name=%(type_name)s"
        request += "\nORDER BY id_pokemon"
        request += f"\nLIMIT {max(limit, 0)} OFFSET {max(offset, 0)}"

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(request,
                            {'type_id': type_id
                                , 'type_name': type_name})
                results = curs.fetchall()

        pokemons = []
        for res in results:
            attack = PokemonModelShort(
                name=res.get("name")
                ,id=res.get("id_pokemon")
                ,pokemon_type=res.get("pokemon_type_name")
                ,url_image=res.get("url_image")

            )
            pokemons.append(attack)
        return pokemons

    
    def find_by_id(self, id: int) -> PokemonModelFull:
        return self.__find_by_name_or_id(id=id)
    
    def find_by_name(self, pokemon_name: str) -> PokemonModelFull:
        return self.__find_by_name_or_id(name=pokemon_name)

    def find_pokemon_id(self, name:str="", id:int=0)-> int:
        requete ="SELECT id_pokemon"\
                 "\nFROM pokemon"
        if name:
            requete+= "\n\t WHERE name=%(name)s"
        else :
            requete+= "\n\t WHERE id_pokemon=%(id)s"

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(
                    requete
                    , {"id": id,"name":name})
                res = curs.fetchone()
        id=None
        if res is not None:
            id = res["id_pokemon"]
        return id

    def __find_by_name_or_id(self, name:str="", id:int=0) -> PokemonModelFull:
        requete ="SELECT pokemon_type_name,name, id_pokemon,level"\
                 ",hp, attack, defense, spe_atk, spe_def, speed, url_image"\
                 "\nFROM pokemon JOIN pokemon_type type ON pokemon.id_pokemon_type=type.id_type_pokemon"
        if name:
            requete+= "\n\t WHERE name=%(name)s"
        else :
            requete+= "\n\t WHERE id_pokemon=%(id)s"
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(
                    requete
                    , {"id": id,"name":name})
                res = curs.fetchone()
        
        pokemon = None
        # Check if we find a pokemon. Is not, the function will end
        if res is not None:
            pokemon = PokemonModelFull(
                name =res["name"]
                ,id=res["id_pokemon"]
                ,pokemon_type=res["pokemon_type_name"]
                ,level =res["level"]
                ,url_image=res["url_image"]
                ,statistic = Statistics(
                    hp=res["hp"]
                    ,attack=res["attack"]
                    ,defense=res["defense"]
                    ,spe_atk=res["spe_atk"]
                    ,spe_def=res["spe_def"]
                    ,speed=res["speed"]
                    )
                , attacks = AttackDao.find_all_attacks_by_pokemon_id(res["id_pokemon"])
            )

        return pokemon


    def update(self, pokemon, id_to_update) :
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                id_type = self.get_id_type_pokemon(pokemon, curs)

                try:
                    curs.execute(
                        "WITH updated AS ("
                        "UPDATE pokemon "
                        "\n SET name=%(name)s"
                        "\n\t\t, hp=%(hp)s"
                        "\n\t\t, attack=%(attack)s"
                        "\n\t\t, defense=%(defense)s"
                        "\n\t\t, spe_atk=%(spe_atk)s"
                        "\n\t\t, spe_def=%(spe_def)s"
                        "\n\t\t, speed=%(speed)s"
                        "\n\t\t, id_pokemon_type=%(id_pokemon_type)s"
                        "\n\t\t, level=%(level)s"
                        "\n\t\t, url_image=%(url_image)s"
                        "\n\t WHERE id_pokemon = %(id_pokemon)s"
                        "\n\t RETURNING *)"
                        "SELECT pokemon_type_name,name, id_pokemon,level"
                        ",hp, attack, defense, spe_atk, spe_def, speed, url_image"
                        "\nFROM updated JOIN pokemon_type type ON updated.id_pokemon_type=type.id_type_pokemon"
                        , {"id_pokemon" : id_to_update
                           ,'name' : pokemon.name
                           ,'hp' : pokemon.statistics.hp
                           ,'attack' : pokemon.statistics.attack 
                           ,'defense' : pokemon.statistics.defense 
                           ,'spe_atk' : pokemon.statistics.spe_atk
                           ,'spe_def' : pokemon.statistics.spe_def 
                           ,'speed' : pokemon.statistics.speed
                           ,'id_pokemon_type' : id_type
                           ,'level' : pokemon.level
                           ,'url_image' : pokemon.url_image})
                except psycopg2.errors.UniqueViolation:
                    raise ResourceAlreadyExistException(pokemon)
                result = curs.fetchone()
        pokemon_out = PokemonModelFull(
                name =pokemon.name
                ,id=result['id_pokemon']
                ,pokemon_type=pokemon.pokemon_type
                ,level =pokemon.level
                ,url_image=pokemon.url_image
                ,statistic = Statistics(
                    hp=pokemon.statistics.hp
                    ,attack=pokemon.statistics.attack
                    ,defense=pokemon.statistics.defense
                    ,spe_atk=pokemon.statistics.spe_atk
                    ,spe_def=pokemon.statistics.spe_def
                    ,speed=pokemon.statistics.speed
                    )
                , attacks = [])
        return pokemon_out

    def get_id_type_pokemon(self, pokemon, curs):
        curs.execute("SELECT id_type_pokemon "
                "\n\tFROM pokemon_type"
                "\n\tWHERE pokemon_type_name = %(pokemon_type)s"
                , {"pokemon_type": pokemon.pokemon_type})
        id_type = curs.fetchone()['id_type_pokemon']
        return id_type

    def create(self, pokemon) :
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                id_type = self.get_id_type_pokemon(pokemon, curs)

                try:
                    curs.execute(
                        "INSERT INTO pokemon "
                        "(name ,hp, attack, defense, spe_atk,"
                        " spe_def, speed, id_pokemon_type, level, url_image) VALUES "
                        "\n\f(%(name)s, %(hp)s,%(attack)s"
                        ", %(defense)s, %(spe_atk)s, %(spe_def)s"
                        ", %(speed)s, %(id_pokemon_type)s, %(level)s, %(url_image)s)"
                        "RETURNING id_pokemon"
                        , {'name' : pokemon.name
                           ,'hp' : pokemon.statistics.hp
                           ,'attack' : pokemon.statistics.attack 
                           ,'defense' : pokemon.statistics.defense 
                           ,'spe_atk' : pokemon.statistics.spe_atk
                           ,'spe_def' : pokemon.statistics.spe_def 
                           ,'speed' : pokemon.statistics.speed
                           ,'id_pokemon_type' : id_type
                           ,'level' : pokemon.level
                           ,'url_image' : pokemon.url_image})
                except psycopg2.errors.UniqueViolation:
                    raise ResourceAlreadyExistException(pokemon)
                result = curs.fetchone()
        pokemon_out = PokemonModelFull(
                name =pokemon.name
                ,id=result['id_pokemon']
                ,pokemon_type=pokemon.pokemon_type
                ,level =pokemon.level
                ,url_image=pokemon.url_image
                ,statistic = Statistics(
                    hp=pokemon.statistics.hp
                    ,attack=pokemon.statistics.attack
                    ,defense=pokemon.statistics.defense
                    ,spe_atk=pokemon.statistics.spe_atk
                    ,spe_def=pokemon.statistics.spe_def
                    ,speed=pokemon.statistics.speed
                    )
                , attacks = [])
        return pokemon_out
        

    def delete(self, business_object) -> bool:
        return super().delete(business_object)

    def add_attack_to_pokemon(self,id_pokemon:int, id_attack:int, level:int)->bool:
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                  curs.execute(
                        "INSERT INTO pokemon_attack(id_pokemon, id_attack, level) "
                        "VALUES (%(id_pokemon)s, %(id_attack)s, %(level)s)",
                        {
                            "id_pokemon":id_pokemon
                            ,"id_attack":id_attack
                            ,"level":level
                        })
