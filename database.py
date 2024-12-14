import logging
from neo4j import GraphDatabase
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DBHandler:
    def __init__(self, connection_uri, username, pwd):
        self.db_driver = GraphDatabase.driver(connection_uri, auth=(username, pwd))

    def shutdown(self):
        self.db_driver.close()

    def execute_query(self, q, params=None):
        with self.db_driver.session() as session:
            try:
                res = session.run(q, params)
                return [r for r in res]
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise HTTPException(status_code=500, detail="Query execution error")

    # Пример методов
    def add_user(self, user_info):
        query = """
        MERGE (u:User {id: $id})
        SET u.name = $name, u.screen_name = $screen_name, u.sex = $sex, u.city = $city
        """
        self.execute_query(query, user_info)

    def run_custom_query(self, query_type):
        queries = {
            'users_count': "MATCH (u:User) RETURN COUNT(u) AS count",
            # Добавить остальные запросы
        }
        try:
            return self.execute_query(queries[query_type])
        except KeyError:
            logger.error("Query type not found")
            return []
