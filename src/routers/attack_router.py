from typing import Optional, List, Union

from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from dao.attack_dao import AttackDao
from exception.resource_already_exist_exception import ResourceAlreadyExistException
from exception.unkwown_attack_type_exception import UnknownAttackTypeException
from models.attack_models import AttackModelOut, AttackModelIn
from models.list_attack_model import ListAttackModel
from models.message import Message
from models.type_attack_name_model import TypeAttackNameModel

__PREFIX = "/attack"

router = APIRouter(
    prefix=__PREFIX,
    tags=["attack"],
    responses={404: {"description": "`Attack` not found"}},
)


@router.get("/", tags=["attack"]
    , description="Return all `Attack` stored in the application."
                  "You can customize your query with these *query parameters*"
                  "<br />- `type_attack_id` (optional, int) : filter your query by attack"
                  " type id. For this lab, this parameter must in [1,3]."
                  "<br />- `type_attack_name` (optional, str) filter your query by attack"
                  " type name"
                  "<br />- `limit` How many attacks the call will return (default 100)"
                  "<br />- `offset`How many attacks you wan to skip"
                  "<br /> If type_attack_id and type_attack_name are both specified,"
                  " type_attack_id is used"
    , response_model_exclude_defaults=True
    , response_model=ListAttackModel)
async def get_all_attacks(
        type_attack_id: Optional[int] = Query(None
            , description="Filter by attack type id."
                          "For this lab, this parameter must in [1,3]."
            , ge=1, le=4)
        , type_attack_name: Optional[TypeAttackNameModel] = Query(None
            , description="Filter by attack type name.")
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
    attack_dao = AttackDao()
    # Check if there is a filter field
    if type_attack_id:
        attacks = attack_dao.find_all(type_id=type_attack_id, limit=limit, offset=offset)
    elif type_attack_name:
        attacks = attack_dao.find_all(type_name=type_attack_name, limit=limit, offset=offset)
    else:
        attacks = attack_dao.find_all(limit=limit, offset=offset)

    # Convert the attack business object in model representation
    for attack in attacks:
        attack.url = f'{__PREFIX}/{attack.name}'
    result = ListAttackModel(count=len(attacks), results=attacks)
    return result


@router.get("/{attack_name_or_id}", tags=["attack"]
    , description="Return the `Attack` resource with the specified name."
    , response_model=AttackModelOut)
async def get_attack_by_name(
        attack_name_or_id: Union[int, str] = Path(...
            , description="The `Attack` name"
            , example="Dragon Rage")):
    attack_dao = AttackDao()
    if isinstance(attack_name_or_id, int):
        attack = attack_dao.find_by_id(attack_name_or_id)
    elif isinstance(attack_name_or_id, str):
        attack = attack_dao.find_by_name(attack_name_or_id)
    # Is attack is None, there is no attack in the db with this name
    if attack is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
    attack.url = f'{__PREFIX}/{attack.name}'
    return attack


@router.post("/", tags=["attack"]
    , status_code=201
    , description="Create a new attack based on the body provided."
                  "If an `Attack` with the same name already exists, "
                  "the insertion fails and you will get a status code "
                  "`409` conflict. If you want to update an "
                  "`Attack` see [/attack/update_attack](#/attack/update_attack)"
    , response_model=AttackModelOut
    , responses={
        400: {"model": Message, "description": "The attack type is unknown"},
        409: {"model": Message, "description": "An attack with this name already exists"},
    })
async def add_new_attack(
        attack: AttackModelIn = Body(
            ..., description="The `Attack` you want to add to the application."

        )):
    attack_dao = AttackDao()
    try:
        attack = attack_dao.create(attack)
    except ResourceAlreadyExistException:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT
                            , content={"message": "An attack with this name already exists"})
    return AttackModelOut(name=attack.name
                          , id=attack.id
                          , power=attack.power
                          , description=attack.description
                          , attack_type=attack.attack_type
                          , url=f'{__PREFIX}/{attack.name}')


@router.put("/{attack_name_or_id}", tags=["attack"]
    , description="Update the `Attack` with the given name. If no"
                  "`Attack` with this name exists, the resource"
                  "is created and you will receive an status code"
                  "`201`."
    , operation_id="update_attack")
async def update_attack(attack_name: str, attack_model: AttackModelIn):
    # Create an attack
    attack_model.name = attack_name
    attack_dao = AttackDao()
    if attack_dao.find_by_name(attack_name):
        attack = attack_dao.update(attack_model)
    else:
        attack = attack_dao.create(attack_model)

    return AttackModelOut(name=attack.name
                          , id=attack.id
                          , power=attack.power
                          , description=attack.description
                          , attack_type=attack.attack_type
                          , url=f'{__PREFIX}/{attack.name}')


@router.delete("/{attack_name_or_id}", tags=["attack"]
    , description=""
    , status_code=200)
async def delete_attack(attack_name_or_id: Union[int, str] = Path(...
    , description="The `Attack` name"
    , example="Dragon rage")):
    attack_dao = AttackDao()
    deleted = False
    if isinstance(attack_name_or_id, int):
        deleted: bool = attack_dao.delete(attack_id=attack_name_or_id)
    elif isinstance(attack_name_or_id, str):
        deleted: bool = attack_dao.delete(attack_name=attack_name_or_id)
    if not deleted:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
