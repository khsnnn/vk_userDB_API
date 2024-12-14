from pydantic import BaseModel
from typing import Dict, Any

class UserModel(BaseModel):
    user_id: str
    depth: int = 2

class NodeModel(BaseModel):
    label: str
    id: int
    attributes: Dict[str, Any]

class RelationshipModel(BaseModel):
    from_node: str
    to_node: str
    relationship_type: str
    attributes: Dict[str, Any]
