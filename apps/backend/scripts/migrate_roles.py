import asyncio
import sys
import os

# Add the root of the project to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from config.settings import settings
from infrastructure.database.models import Family, FamilyMember

async def migrate_roles():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        families_res = await session.execute(select(Family))
        families = families_res.scalars().all()
        
        for family in families:
            members_res = await session.execute(
                select(FamilyMember).where(FamilyMember.family_id == family.id)
            )
            members = members_res.scalars().all()
            
            for member in members:
                # Default role logic
                if member.is_primary:
                    role = "owner"
                else:
                    # simplistic adult vs minor check based on relationship or dob
                    rel = member.relationship.lower()
                    if rel in ["child", "son", "daughter", "nephew", "niece"]:
                        # check dob if possible, but relationship implies minor for now in demo
                        role = "minor"
                    else:
                        role = "standard"
                
                member.role = role
                session.add(member)
                
        await session.commit()
        print("Migrated roles successfully.")

if __name__ == "__main__":
    asyncio.run(migrate_roles())
