from psycopg2.extras import RealDictCursor

import psycopg2

from utils.singleton import Singleton


class ConnectionManager(metaclass=Singleton):
    """
    ConnectionManager handles tthe database connection. It's a technical
    class, so DO NOT MODIFY IT ! You can use this class for your
    project if you want.

    This class is a singleton, so there is only one instance of
    PoolConnection in your code. Why ? Because we do not want to open
    too much connection.

    If you want a connection juste call getConnection.

    """
    __connection= None

    @staticmethod
    def getConnexion():
        """
        C'est la méthode que l'on va utiliser si l'on veut obtenir l'instance
        de de ReservoirConnexion
        :return: le singleton ReservoirConnexion
        :rtype: PoolConnection
        """
        if ConnectionManager.__connection is None:
            ConnectionManager()
        return ConnectionManager.__connection

    def __init__(self, host, port, database, user, password):
        """
        If there is no connection, one is creted, else an exception
        is raised.

        """
        if ConnectionManager.__connection != None :
            raise Exception("A connection already exist")
        else:
            ConnectionManager.__connection = psycopg2.connect(host=host,
                                                              port=port,
                                                              database=database,
                                                              user=user,
                                                              password=password,
                                                              cursor_factory=RealDictCursor
                                                              )
