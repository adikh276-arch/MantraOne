from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from core.services.family_service import FamilyService

router = APIRouter()


@router.post("/")
async def create_family(
    name: str, primary_member_name: str, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)
):
    service = FamilyService(db)
    family = await service.create_family(name=name, firebase_uid=user["uid"], primary_member_name=primary_member_name)
    return {"id": family.id}


@router.get("/")
async def list_families(db: AsyncSession = Depends(get_db)):
    # Quick hack to return all families for demo
    from sqlalchemy import select
    from infrastructure.database.models import Family

    result = await db.execute(select(Family))
    families = result.scalars().all()
    return [{"id": f.id, "name": f.name} for f in families]
