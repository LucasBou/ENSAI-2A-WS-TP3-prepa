from abc import ABC
from typing import List, Any

from utils.singleton_abcmeta import SingletonABCMeta


class AbstractDao():
    """
    Abstract class that all dao classes must inherit. Give all the
    standards methods of a dao (CRUD). We want to normalize the
    behaviour of the dao.
    This class is a singleton too, because all it's child must
    be singleton too.
    """
    __metaclass__ = SingletonABCMeta

    def find_by_id(self, id:int) -> Any:
        """Find one element in the db by it's id"""
        return NotImplementedError

    def find_all(self) -> List[Any]:
        """Return all the element of the db"""
        return NotImplementedError

    def update(self, business_object:Any) -> Any:
        """Update one row in the db"""
        return NotImplementedError

    def create(self, business_object:Any) -> Any:
        """Add one row in the db"""
        return NotImplementedError

    def delete(self, business_object) -> bool:
        """
        Delete one row
        :return if a line was deleted
        :rtype bool
        """
        return NotImplementedError
