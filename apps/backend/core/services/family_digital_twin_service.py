from uuid import UUID
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.domain.entities import FamilyDigitalTwin, PreventiveObservationContext
from core.services.knowledge_projection_service import KnowledgeProjectionService
from core.services.health_state_engine import HealthStateEngine

class FamilyDigitalTwinService:
    """
    Constructs the master FamilyDigitalTwin aggregate object from the Knowledge Projection
    and deterministic Health States. This is the single source of truth for the API and frontend.
    """
    
    def __init__(self, db: AsyncSession):
        self._db = db
        self._graph_service = KnowledgeProjectionService(db)
        self._state_engine = HealthStateEngine(db)

    async def get_digital_twin(self, family_id: UUID) -> FamilyDigitalTwin:
        """
        Builds the complete twin.
        """
        graph = await self._graph_service.build_family_graph(family_id)
        
        twin = FamilyDigitalTwin(family_id=family_id)
        
        for member_id_str, member_node in graph["members"].items():
            member_id = UUID(member_id_str)
            
            # Demographics
            twin.members.append({
                "id": member_node["id"],
                "name": member_node["name"],
                "relationship": member_node["relationship"]
            })
            
            # Health State
            health_state = await self._state_engine.compute_state(member_id)
            twin.health_states[member_id_str] = health_state
            
            # Confidences (mapped from graph)
            twin.confidence_scores[member_id_str] = member_node["confidences"]
            
            # Insights, Follow-ups, and Preventive Needs
            twin.insights[member_id_str] = member_node["insights"]
            twin.follow_ups[member_id_str] = member_node["follow_ups"]
            
            # We map PreventiveNeeds to the specific context model
            prevs = []
            for p in member_node["preventive_needs"]:
                # The graph projection simplified it, we can just pack it loosely or query DB for full
                prevs.append(
                    PreventiveObservationContext(
                        id=UUID(int=0), # Placeholder for graph projection mapping
                        observation_type=p["type"],
                        description=p["desc"],
                        status="active",
                        created_at=health_state.get("generated_at", None) or "2026-06-26T00:00:00Z" # type: ignore
                    )
                )
            twin.preventive_needs[member_id_str] = prevs
            
            # Missing Info comes from health state
            twin.missing_information[member_id_str] = health_state.get("missing_information", [])
            
        return twin
