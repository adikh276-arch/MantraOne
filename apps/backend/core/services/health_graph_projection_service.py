from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models import FamilyMember, Document, Medication, Diagnosis, HealthMetric

class HealthGraphProjectionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        from core.providers.encryption_service import EncryptionService
        self.enc = EncryptionService()

    def _safe_decrypt(self, text: str | None) -> str:
        if not text:
            return "Unknown"
        try:
            return self.enc.decrypt(text)
        except Exception:
            return text

    async def get_family_graph(self, family_id: UUID) -> dict:
        nodes = []
        edges = []

        # Fetch Members
        members = await self.db.execute(select(FamilyMember).where(FamilyMember.family_id == family_id))
        member_map = {}
        for member in members.scalars().all():
            nodes.append({
                "id": str(member.id),
                "label": self._safe_decrypt(member.name),
                "type": "person",
                "metadata": {"relationship": member.relationship}
            })
            member_map[member.id] = str(member.id)

        # Fetch Diagnoses
        diagnoses = await self.db.execute(select(Diagnosis).where(Diagnosis.family_id == family_id))
        for diagnosis in diagnoses.scalars().all():
            diag_id = f"diag_{diagnosis.id}"
            nodes.append({
                "id": diag_id,
                "label": self._safe_decrypt(diagnosis.condition_name),
                "type": "condition",
                "metadata": {"status": diagnosis.status}
            })
            if diagnosis.member_id in member_map:
                edges.append({
                    "source": member_map[diagnosis.member_id],
                    "target": diag_id,
                    "label": "has_diagnosis"
                })
            if diagnosis.diagnosed_by:
                doc_node = f"doc_{diagnosis.diagnosed_by}"
                if not any(n["id"] == doc_node for n in nodes):
                    nodes.append({"id": doc_node, "label": diagnosis.diagnosed_by, "type": "doctor"})
                edges.append({"source": doc_node, "target": diag_id, "label": "diagnosed"})

        # Fetch Medications
        medications = await self.db.execute(select(Medication).where(Medication.family_id == family_id))
        for med in medications.scalars().all():
            med_id = f"med_{med.id}"
            nodes.append({
                "id": med_id,
                "label": self._safe_decrypt(med.name),
                "type": "medication",
                "metadata": {"dosage": med.dosage, "status": "active" if med.is_active else "inactive"}
            })
            if med.member_id in member_map:
                edges.append({
                    "source": member_map[med.member_id],
                    "target": med_id,
                    "label": "prescribed"
                })
            # Try to link to a diagnosis if we can infer or if there's an indication
            if med.indication:
                # Basic string matching for indication to condition_name (in a real app, this would use semantic link or FK)
                for n in nodes:
                    if n["type"] == "condition" and n["label"].lower() in med.indication.lower():
                        edges.append({"source": n["id"], "target": med_id, "label": "treats"})

        # Fetch Documents (Reports)
        documents = await self.db.execute(select(Document).where(Document.family_id == family_id))
        for doc in documents.scalars().all():
            doc_id = f"doc_{doc.id}"
            nodes.append({
                "id": doc_id,
                "label": self._safe_decrypt(doc.original_filename) if doc.original_filename else doc.document_type,
                "type": "document",
                "metadata": {"type": doc.document_type, "status": doc.processing_status}
            })
            if doc.member_id in member_map:
                edges.append({
                    "source": member_map[doc.member_id],
                    "target": doc_id,
                    "label": "owns_document"
                })

        # Fetch Health Metrics
        metrics = await self.db.execute(select(HealthMetric).where(HealthMetric.family_id == family_id))
        for metric in metrics.scalars().all():
            metric_id = f"metric_{metric.id}"
            nodes.append({
                "id": metric_id,
                "label": f"{metric.metric_type}: {metric.value_numeric} {metric.unit or ''}".strip(),
                "type": "metric",
                "metadata": {"type": metric.metric_type, "value": metric.value_numeric, "date": metric.recorded_at.isoformat()}
            })
            if metric.member_id in member_map:
                edges.append({
                    "source": member_map[metric.member_id],
                    "target": metric_id,
                    "label": "recorded_metric"
                })
            if metric.source_document_id:
                edges.append({
                    "source": f"doc_{metric.source_document_id}",
                    "target": metric_id,
                    "label": "extracted_from"
                })

        return {
            "nodes": nodes,
            "edges": edges
        }
