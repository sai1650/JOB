from fastapi import APIRouter
from app.core.roles import list_roles, get_role

router = APIRouter()


@router.get("/roles")
def get_roles():
    return {"roles": list_roles()}


@router.get("/roles/{role_id}")
def get_role_by_id(role_id: str):
    role = get_role(role_id)
    if not role:
        return {"error": "not found"}
    return {"id": role_id, **role}
