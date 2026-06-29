import structlog
from typing import Dict, Any
from uuid import UUID

from infrastructure.database.session import get_async_session
from core.services.clinical_context_builder import ClinicalContextBuilder
from core.services.health_insight_service import HealthInsightService
from core.services.follow_up_service import FollowUpService
from core.services.confidence_calculator import ConfidenceCalculator
from infrastructure.database.models import DomainConfidence
from sqlalchemy import select

logger = structlog.get_logger()

async def process_memory_updated_event(ctx: Dict[str, Any], family_id: UUID, member_id: UUID, new_data_text: str, entities: list[dict], memory_type: str) -> None:
    """
    ARQ worker task triggered by the MEMORY_UPDATED event.
    Orchestrates the entire Intelligence Pipeline asynchronously.
    """
    logger.info("intelligence_pipeline_started", family_id=str(family_id), member_id=str(member_id))
    
    # Run the intelligence pipeline in a single DB session
    async for db in get_async_session():
        
        # 1. Update Domain Confidence and Freshness
        conf_calc = ConfidenceCalculator()
        for entity in entities:
            domain = entity.get("type", "general")
            res = await db.execute(select(DomainConfidence).where(
                DomainConfidence.member_id == member_id, 
                DomainConfidence.domain == domain
            ))
            conf_record = res.scalar_one_or_none()
            if not conf_record:
                conf_record = DomainConfidence(family_id=family_id, member_id=member_id, domain=domain)
                db.add(conf_record)
                
            conf_calc.update_domain_confidence(conf_record, new_evidence_confidence=0.9, memory_type=memory_type)
        await db.commit()

        # 2. Re-compute Health State (Deterministic)
        from core.services.health_state_engine import HealthStateEngine
        state_engine = HealthStateEngine(db)
        await state_engine.compute_state(member_id)
        
        # 3. Preventive Intelligence (Proactive Scanning)
        from core.services.preventive_intelligence_service import PreventiveIntelligenceService
        prev_service = PreventiveIntelligenceService(db)
        await prev_service.scan_for_preventive_gaps(member_id, family_id)

        # 4. Generate Structured Insights & Explainability Trace
        insight_service = HealthInsightService(db)
        # Assuming current_context_summary can be a simple string for this phase
        await insight_service.generate_insights(
            member_id=member_id, 
            family_id=family_id, 
            new_data=new_data_text, 
            current_context_summary="Triggered from Event Pipeline"
        )
        
        # 5. Plan Follow-ups deterministically
        followup_service = FollowUpService(db)
        await followup_service.schedule_follow_ups(member_id, family_id, entities)
        
        # 6. Longitudinal Reasoning 
        from core.services.longitudinal_reasoning_service import LongitudinalReasoningService
        long_service = LongitudinalReasoningService(db)
        await long_service.analyze_trajectory(member_id, family_id)
        
        # 7. Timeline Chapters
        from core.services.timeline_intelligence_service import TimelineIntelligenceService
        timeline_service = TimelineIntelligenceService(db)
        await timeline_service.get_intelligent_timeline(member_id)

        # 8. ADAPTIVE INTELLIGENCE LOOP (Decision Engine)
        # We need the most up-to-date twin for the decision engine.
        from core.services.family_digital_twin_service import FamilyDigitalTwinService
        from core.services.decision_engine import DecisionEngine
        
        twin_service = FamilyDigitalTwinService(db)
        updated_twin = await twin_service.get_digital_twin(family_id)
        
        decision_engine = DecisionEngine(db)
        next_action = await decision_engine.determine_next_action(updated_twin, member_id)
        
        logger.info("decision_engine_output", 
            family_id=str(family_id), 
            member_id=str(member_id),
            action_type=next_action.action_type,
            priority=next_action.priority
        )

    logger.info("intelligence_pipeline_completed", family_id=str(family_id), member_id=str(member_id))
