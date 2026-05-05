from fastapi import APIRouter
from services.data_store import list_authority

router = APIRouter()


@router.get("")
@router.get("/")
def get_authority():
    return list_authority()
