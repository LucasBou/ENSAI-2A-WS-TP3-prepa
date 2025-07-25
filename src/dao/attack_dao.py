from typing import List, Any, Optional

import psycopg2 as psycopg2

from dao.abstract_dao import AbstractDao
from dao.connection_manager import ConnectionManager
from exception.resource_already_exist_exception import ResourceAlreadyExistException
from models.attack_models import AttackModelOutShort, AttackModelOut


class AttackDao(AbstractDao):
    def find_all(self, type_id: Optional[int] = None, type_name: Optional[str] = None
                 , limit: int = 100, offset: int = 0) -> List[AttackModelOutShort]:
        request = f"SELECT id_attack, attack_type_name, attack_name" \
                  "\nFROM attack JOIN attack_type type ON attack.id_attack_type=type.id_type_attack"

        if type_id is not None:
            request += "\nWHERE id_attack_type=%(type_id)s"
        elif type_name is not None:
            request += "\nWHERE attack_type_name=%(type_name)s"
        request += "\nORDER BY id_attack"
        request += f"\nLIMIT {max(limit, 0)} OFFSET {max(offset, 0)}"

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(request,
                            {'type_id': type_id
                                , 'type_name': type_name})
                results = curs.fetchall()

        attacks = []
        for res in results:
            attack = AttackModelOutShort(
                id=res.get("id_attack")
                , attack_type=res.get("attack_type_name")
                , name=res.get("attack_name")
            )
            attacks.append(attack)
        return attacks

    def find_by_id(self, id: int) -> AttackModelOut:
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(
                    "SELECT id_attack,attack_type_name, power,accuracy, element, attack_name, attack_description"
                    "\n\tFROM attack JOIN attack_type type ON attack.id_attack_type=type.id_type_attack"
                    "\n\t WHERE id_attack=%(id)s"
                    , {"id": id})
                res = curs.fetchone()

        attack = None
        if res is not None:
            attack = AttackModelOut(
                name=res["attack_name"]
                , id=res["id_attack"]
                , attack_type=res["attack_type_name"]
                , power=res["power"]
                , accuracy=res["accuracy"]
                , element=res["element"]
                , description=res["attack_description"]
            )
        return attack

    def find_by_name(self, attack_name: str) -> AttackModelOut:
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(
                    "SELECT id_attack,attack_type_name, power,accuracy, element, attack_name, attack_description"
                    "\n\tFROM attack JOIN attack_type type ON attack.id_attack_type=type.id_type_attack"
                    "\n\t WHERE attack_name=%(attack_name)s"
                    , {"attack_name": attack_name})
                res = curs.fetchone()

        attack = None
        if res is not None:
            attack = AttackModelOut(
                name=res["attack_name"]
                , id=res["id_attack"]
                , attack_type=res["attack_type_name"]
                , power=res["power"]
                , accuracy=res["accuracy"]
                , element=res["element"]
                , description=res["attack_description"]
            )
        return attack

    def update(self, attack: AttackModelOut) -> AttackModelOut:
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute("SELECT id_type_attack "
                             "\n\tFROM attack_type"
                             "\n\tWHERE attack_type_name = %(attack_type)s"
                             , {"attack_type": attack.attack_type})
                id_type = curs.fetchone()['id_type_attack']
                curs.execute(
                    "WITH updated AS ("
                    "\n\t UPDATE attack SET"
                    "\n\t\t  id_attack_type = %(id_type)s"
                    "\n\t\t, power=%(power)s"
                    "\n\t\t, attack_description = %(attack_description)s"
                    "\n\t\t, accuracy=%(accuracy)s"
                    "\n\t\t, element=%(element)s"
                    "\n\t WHERE attack_name = %(attack_name)s"
                    "\n\t RETURNING *)"
                    "SELECT id_attack,attack_type_name, power,accuracy, element, attack_name, attack_description"
                    "\n\t FROM updated JOIN attack_type type ON updated.id_attack_type=type.id_type_attack"
                    , {'power': attack.power
                        , 'attack_name': attack.name
                        , 'attack_description': attack.description
                        , 'id_type': id_type
                        , 'accuracy': attack.accuracy
                        , 'element': attack.element})
                res = curs.fetchone()

        if res is not None:
            attack = AttackModelOut(
                name=res["attack_name"]
                , id=res["id_attack"]
                , attack_type=res["attack_type_name"]
                , power=res["power"]
                , accuracy=res["accuracy"]
                , element=res["element"]
                , description=res["attack_description"]
            )
        return attack

    def create(self, attack: AttackModelOut) -> AttackModelOut:
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute("SELECT id_type_attack "
                             "\n\tFROM attack_type"
                             "\n\tWHERE attack_type_name = %(attack_type)s"
                             , {"attack_type": attack.attack_type})
                id_type = curs.fetchone()['id_type_attack']
                try:
                    curs.execute(
                        "INSERT INTO attack "
                        "(id_attack_type, power,accuracy, element, attack_name, attack_description) VALUES "
                        "\n\f(%(id_attack_type)s, %(power)s,%(accuracy)s"
                        ", %(element)s, %(attack_name)s, %(attack_description)s)"
                        "RETURNING id_attack"
                        , {'power': attack.power
                            , 'attack_name': attack.name
                            , 'attack_description': attack.description
                            , 'id_attack_type': id_type
                            , 'accuracy': attack.accuracy
                            , 'element': attack.element})
                except psycopg2.errors.UniqueViolation:
                    raise ResourceAlreadyExistException(attack)
                result = curs.fetchone()['id_attack']
        attack.id = result
        return attack

    def delete(self, attack_name: Optional[str] = None
               , attack_id: Optional[str] = None) -> bool:
        deleted = False
        request = "DELETE FROM attack "
        if attack_name is not None:
            request += "WHERE attack_name = %(attack_name)s"
        elif attack_id is not None:
            request += "WHERE id_attack = %(attack_id)s"
        else:
            return deleted
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(request
                             , {"attack_id": attack_id
                                 , "attack_name": attack_name})
                if curs.rowcount > 0:
                    deleted = True
        return deleted


    def find_all_attacks_by_pokemon_id(id_pokemon : int
        )-> List[AttackModelOutShort]:
        request = f"SELECT id_attack, attack_type_name, attack_name" \
                  "\nFROM attack JOIN attack_type type ON attack.id_attack_type=type.id_type_attack"\
                  "\n\t JOIN pokemon_attack USING(id_attack)"\
                  "\n\t WHERE id_pokemon=%(id_pokemon)s"\
                  "\nORDER BY id_attack"

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs :
                curs.execute(request,
                            {'id_pokemon': id_pokemon})
                results = curs.fetchall()

        attacks = []
        for res in results:
            attack = AttackModelOutShort(
                id=res.get("id_attack")
                , attack_type=res.get("attack_type_name")
                , name=res.get("attack_name")
                , url = f"attack/{res.get('attack_name')}"
            )
            attacks.append(attack)
        return attacks
