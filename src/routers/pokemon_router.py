from dao.attack_dao import AttackDao
from exception.resource_already_exist_exception import ResourceAlreadyExistException
from models.pokemon_model import PokemonModelIn, TypePokemon
from models.message import Message
from starlette import status
from models.statistics import Statistics
from fastapi.param_functions import Body, Path
from starlette.responses import JSONResponse
from models.pokemon_model import PokemonModelFull
from typing import Optional, Union

from fastapi import APIRouter, Query
from enum import Enum

from dao.pokemon_dao import PokemonDao
from models.list_pokemon_model import ListPokemonModel

__PREFIX = "/pokemon"

router = APIRouter(
    prefix=__PREFIX,
    tags=["pokemon"],
    responses={404: {"description": "`pokemon` not found"}},
)


@router.get("/", tags=["pokemon"]
    , description="Return all `Pokemons` stored in the application."\
                  "You can customize your query with these *query parameters*"
                  "<br />- `type_pokemon_id` (optional, int) : filter your query by pokemon"
                  " type id. For this lab, this parameter must in [1,5]."
                  "<br />- `type_pokemon_name` (optional, str) filter your query by pokemon"
                  " type name"
                  "<br />- `limit` How many pokemons the call will return (default 100)"
                  "<br />- `offset`How many pokemons you want to skip"
                  "<br /> If type_attack_id and type_attack_name are both specified,"
                  " type_attack_id is used"
    , response_model_exclude_defaults=True
    , response_model=ListPokemonModel)
async def get_all_pokemons(
        type_pokemon_id: Optional[int] = Query(None
            , description="Filter by pokemon type id."
                          "For this lab, this parameter must in [1,5]."
            , ge=1, le=5)
        , type_pokemon_name: Optional[TypePokemon] = Query(None
            , description="Filter by pokemon type name.")
        , limit: Optional[int] = Query(100
            , description="If a limit count is given, no more than that many "
                          "rows will be returned (but possibly less, if the "
                          "query itself yields less rows)")
        , offset: Optional[int] = Query(0
            , description="OFFSET says to skip that many rows before beginning to "
                          "return rows. OFFSET 0 is the same as omitting the OFFSET "
                          "clause. If both OFFSET and LIMIT appear, then OFFSET rows "
                          "are skipped before starting to count the LIMIT rows that "
                          "are returned.")):
    pokemon_dao = PokemonDao()

    # Check if there is a filter field
    if type_pokemon_id:
        pokemons = pokemon_dao.find_all(type_id=type_pokemon_id, limit=limit, offset=offset)
    elif type_pokemon_name:
        pokemons = pokemon_dao.find_all(type_name=type_pokemon_name, limit=limit, offset=offset)
    else:
        pokemons = pokemon_dao.find_all(limit=limit, offset=offset)

    for pokemon in pokemons:
        pokemon.url = f'{__PREFIX}/{pokemon.name}'
    result = ListPokemonModel(count=len(pokemons), results=pokemons)
    return result

@router.get("/{pokemon_identifier}", tags=["pokemon"]
    , description="Return the `Pokemon` resource with the specified name or id."
    , response_model=PokemonModelFull)
async def get_pokemon_by_identifier(
        pokemon_identifier: Union[int, str] = Path(...
            , description="The `Pokemon` name"
            , example="Pikachu")):
    pokemon_dao = PokemonDao()
    if isinstance(pokemon_identifier, int):
        pokemon = pokemon_dao.find_by_id(pokemon_identifier)
    elif isinstance(pokemon_identifier, str):
        pokemon = pokemon_dao.find_by_name(pokemon_identifier.title())
    # Is attack is None, there is no pokemon in the db with this name
    if pokemon is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
    pokemon.url = f'{__PREFIX}/{pokemon.name}'
    return pokemon

@router.post("/", tags=["pokemon"]
    , status_code=201
    , description="Create a new pokemon based on the body provided."
                  "If an `Pokemon` with the same name already exists, "
                  "the insertion fails and you will get a status code "
                  "`409` conflict. If you want to update a "
                  "`Pokemon` see [/pokemon/update_pokemon](#/pokemon/update_pokemon)"
    , response_model=PokemonModelFull
    , responses={
        400: {"model": Message, "description": "The pokemon type is unknown"},
        409: {"model": Message, "description": "A pokemon with this name already exists"},
    })
async def add_new_pokemon(
        pokemon: PokemonModelIn = Body(
            ..., description="The `Pokemon` you want to add to the application."

        )):
    pokemon_dao = PokemonDao()
    try:
        pokemon = pokemon_dao.create(pokemon)
    except ResourceAlreadyExistException:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT
                            , content={"message": "A pokemon with this name already exists"})
    return pokemon


@router.put("/{pokemon_identifier}", tags=["pokemon"]
    , description="Update the `Pokemon` with the given identifier. If no"
                  "`Pokemon` with this identifier exists, the resource"
                  "will be created and you will receive an status code"
                  "`201`."
    , operation_id="update_pokemon")
async def update_pokemon(pokemon_identifier: Union[int, str] = Path(...
                , description="The `Pokemon` name"
                , example="Pikachu")
            , pokemon_model:PokemonModelIn = Body(...
                , description="The `Pokemon` json representation")) -> PokemonModelFull:

    pokemon_dao = PokemonDao()
    pokemon_id = None
    if isinstance(pokemon_identifier, int):
        pokemon_id = pokemon_dao.find_pokemon_id(id =pokemon_identifier)
    elif isinstance(pokemon_identifier, str):
        pokemon_id = pokemon_dao.find_pokemon_id(name = pokemon_identifier.title())

    if pokemon_id:
        pokemon = pokemon_dao.update(pokemon_model, pokemon_id)
    else:
        pokemon = pokemon_dao.create(pokemon_model)

    return pokemon


@router.post("/{pokemon_identifier}/attack", tags=["pokemon"]
    , status_code=201
    , description="Add an `Attack` to a pokemon based on the attack `id`")
async def add_attack_to_pokemon(pokemon_identifier: Union[int, str] = Path(...
                , description="The `Pokemon` name"
                , example="Pikachu")
            , attack_id:int = Body(...
                , description="The `Attack` id")
            , level:int= Body(...
                , description="When the `Pokemon learn the move`")):
    pokemon_dao = PokemonDao()
    pokemon_id = None
    if isinstance(pokemon_identifier, int):
        pokemon_id = pokemon_dao.find_pokemon_id(id =pokemon_identifier)
    elif isinstance(pokemon_identifier, str):
        pokemon_id = pokemon_dao.find_pokemon_id(name = pokemon_identifier.title())

    attack_dao = AttackDao()
    attack = attack_dao.find_by_id(attack_id)

    if pokemon_id and attack:
        pokemon_dao.add_attack_to_pokemon(id_pokemon = pokemon_id
                                          , id_attack= attack_id
                                          , level=level)
    else :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
