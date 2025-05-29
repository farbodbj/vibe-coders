from typing import Literal, Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    gid: str = Field(description="Global ID for this node")
    identifier: str
    file: str
    path: str

    node_type: str

    short_doc: Optional[str] = None


class Relation(BaseModel):
    source: str
    target: str

    short_doc: str


class CommonName(BaseModel):
    type: Literal['http_service', 'grpc_service', 'package']
    name: str


class ProjectKnowledgeBase(BaseModel):
    name: str
    description: str

    common_names: Optional[list[CommonName]] = Field(
        default_factory=list,
        description="Common names that this project might be refered to with")

    nodes: dict[str, Node] = Field(
        default_factory=dict,
        description="References for nodes and definitions in the project")
    relations: dict[tuple[str, str], Relation] = Field(
        default_factory=dict,
        description="Relations inside this project or references to other projects"
    )
