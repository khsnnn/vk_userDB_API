from fastapi import FastAPI, HTTPException, Depends
from database import DBHandler
from auth import validate_token
from typing import Dict
import logging


logging.basicConfig(level='INFO', format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

def register_routes(app: FastAPI, db_handler: DBHandler):
    @app.get("/user/{user_id}")
    async def fetch_user(user_id: str):
        q = "MATCH (u:User {id: toInteger($user_id)}) RETURN u.id, u.name, u.screen_name, u.sex, u.city"
        result = db_handler.execute_query(q, {'user_id': user_id})

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        user = result[0]
        return {
            "id": user['u.id'],
            "name": user['u.name'],
            "screen_name": user['u.screen_name'],
            "sex": user['u.sex'],
            "city": user['u.city']
        }

    @app.get("/top-users")
    async def fetch_top_users():
        q = """
        MATCH (u:User)<-[:FOLLOWS]-()
        RETURN u.id, u.name, COUNT(*) AS followers_count
        ORDER BY followers_count DESC LIMIT 5
        """
        result = db_handler.execute_query(q)
        return [{"id": record["u.id"], "name": record["u.name"], "followers_count": record["followers_count"]} for record in result]

    @app.get("/top-groups")
    async def fetch_top_groups():
        q = """
        MATCH (g:Group)<-[:SUBSCRIBED]-()
        RETURN g.id, g.name, COUNT(*) AS subscribers_count
        ORDER BY subscribers_count DESC LIMIT 5
        """
        result = db_handler.execute_query(q)

        return [{"id": record["g.id"], "name": record["g.name"], "subscribers_count": record["subscribers_count"]} for record in result]

    @app.get("/users-count")
    async def fetch_users_count():
        q = "MATCH (u:User) RETURN COUNT(u) AS count"
        result = db_handler.execute_query(q)

        return {"users_count": result[0]["count"]}

    @app.get("/groups-count")
    async def fetch_groups_count():
        q = "MATCH (g:Group) RETURN COUNT(g) AS count"
        result = db_handler.execute_query(q)

        return {"groups_count": result[0]["count"]}

    @app.get("/nodes")
    async def fetch_all_nodes():
        q = "MATCH (n) RETURN n.id, labels(n) AS label"
        result = db_handler.execute_query(q)

        nodes = [{"id": record["n.id"], "label": record["label"][0]} for record in result]
        return nodes

    @app.get("/node/{label}/{node_id}")
    async def fetch_node_with_relations(label: str, node_id: int):
        """
        Получить узел и его связи по label и id.
        """
        logger.info(f"Fetching node with label: {label} and ID: {node_id}")

        q = f"""
        MATCH (n:{label} {{id: $node_id}})
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, COLLECT(r) AS relationships, COLLECT(m) AS related_nodes
        """
        result = db_handler.execute_query(q, {"node_id": node_id})

        if not result:
            logger.error(f"No results found for node with label: {label} and ID: {node_id}")
            raise HTTPException(status_code=404, detail="Node or relations not found")

        node_data = None
        relations = []

        for record in result:
            node = record['n']
            relationships = record['relationships']
            related_nodes = record['related_nodes']

            if node_data is None:
                node_data = {
                    "label": label,
                    "attributes": dict(node.items())
                }

            for relationship, related_node in zip(relationships, related_nodes):
                relations.append({
                    "relationship": {
                        "type": relationship.type if relationship else None,
                        "attributes": dict(relationship.items()) if relationship else {}
                    },
                    "related_node": {
                        "id": related_node['id'],
                        "label": list(related_node.labels)[0] if related_node.labels else 'No Label',
                        "attributes": dict(related_node.items()) if related_node else {}
                    }
                })

        return {
            "node": node_data,
            "relations": relations
        }

    @app.post("/nodes")
    async def create_node_and_relationships(node_data: dict = None, token: str = Depends(validate_token)):
        
        if not node_data:
            raise HTTPException(status_code=400, detail="No node data provided")

        label = node_data.get("label", "User")

        create_node_query = f"""
        CREATE (u:{label} {{id: $id, label: $label, name: $name,
                            sex: $sex, city: $city, screen_name: $screen_name}})
        RETURN u
        """
        db_handler.execute_query(create_node_query, node_data)

        if "follows" in node_data:
            for follow_id in node_data["follows"]:
                follow_query = """
                MATCH (u:User {id: $id}), (f:User {id: $follow_id})
                CREATE (u)-[:FOLLOWS]->(f)
                """
                db_handler.execute_query(follow_query, {"id": node_data["id"], "follow_id": follow_id})

        if "subscribes" in node_data:
            for subscribe_id in node_data["subscribed"]:
                subscribe_query = """
                MATCH (u:User {id: $id}), (s:User {id: $subscribe_id})
                CREATE (u)-[:SUBSCRIBED]->(s)
                """
                db_handler.execute_query(subscribe_query, {"id": node_data["id"], "subscribe_id": subscribe_id})

        return {"status": "success"}

    @app.delete("/nodes/{label}/{node_id}")
    async def delete_node_and_relations(label: str, node_id: int, token: str = Depends(validate_token)):
        q = f"""
        MATCH (n:{label} {{id: $node_id}})-[r]->()
        DELETE r
        """
        db_handler.execute_query(q, {"node_id": node_id})

        q = f"""
        MATCH (n:{label} {{id: $node_id}})<-[r]-()
        DELETE r
        """
        db_handler.execute_query(q, {"node_id": node_id})

        q = f"""
        MATCH (n:{label} {{id: $node_id}})
        DELETE n
        """
        db_handler.execute_query(q, {"node_id": node_id})

        return {"status": "success"}
