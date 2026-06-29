from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import (
    FamilyMember,
    HealthInsight,
    FollowUp,
    DomainConfidence,
    PreventiveObservation,
)


class KnowledgeProjectionService:
    """
    Projects a deterministic Knowledge Graph in-memory by combining structured relational data
    (PostgreSQL) with semantic insights. Does NOT persist an actual graph database.
    This projection feeds into the FamilyDigitalTwin.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def build_family_graph(self, family_id: UUID) -> Dict[str, Any]:
        """
        Builds the complete Family Knowledge Graph projection.
        Nodes: FamilyMembers, Diagnoses, Medications, FollowUps, Insights, PreventiveNeeds
        Edges are implicit via their nesting/references.
        """
        # Fetch members
        res_mem = await self._db.execute(select(FamilyMember).where(FamilyMember.family_id == family_id))
        members = res_mem.scalars().all()

        graph = {
            "family_id": str(family_id),
            "members": {},
            "cross_member_relationships": [],  # e.g. shared conditions
        }

        for m in members:
            member_node = {
                "id": str(m.id),
                "name": m.name,
                "relationship": m.relationship,
                "confidences": [],
                "insights": [],
                "follow_ups": [],
                "preventive_needs": [],
            }

            # Confidences (proxy for Active Conditions/Domains)
            res_conf = await self._db.execute(select(DomainConfidence).where(DomainConfidence.member_id == m.id))
            confs = res_conf.scalars().all()
            for c in confs:
                member_node["confidences"].append(
                    {"domain": c.domain, "confidence": c.confidence, "freshness": c.freshness}
                )

            # Insights
            res_ins = await self._db.execute(
                select(HealthInsight).where(HealthInsight.member_id == m.id, HealthInsight.status == "active")
            )
            insights = res_ins.scalars().all()
            for i in insights:
                member_node["insights"].append({"type": i.insight_type, "desc": i.description})

            # Follow-ups
            res_fu = await self._db.execute(
                select(FollowUp).where(FollowUp.member_id == m.id, FollowUp.status.in_(["scheduled", "pending"]))
            )
            fus = res_fu.scalars().all()
            for fu in fus:
                member_node["follow_ups"].append(
                    {"desc": fu.description, "due": fu.due_date.isoformat() if fu.due_date else None}
                )

            # Preventive Needs
            res_prev = await self._db.execute(
                select(PreventiveObservation).where(
                    PreventiveObservation.member_id == m.id, PreventiveObservation.status == "active"
                )
            )
            prevs = res_prev.scalars().all()
            for p in prevs:
                member_node["preventive_needs"].append({"type": p.observation_type, "desc": p.description})

            graph["members"][str(m.id)] = member_node

        return graph
