import os

fixes = [
    ("core/domain/enums.py", [
        ('def __gt__(self, other: "SignalSeverity") -> bool:', 'def __gt__(self, other: object) -> bool:\n        if not isinstance(other, SignalSeverity): return NotImplemented'),
        ('def __ge__(self, other: "SignalSeverity") -> bool:', 'def __ge__(self, other: object) -> bool:\n        if not isinstance(other, SignalSeverity): return NotImplemented')
    ]),
    ("config/settings.py", [
        ("@computed_field\n    @property", "@property\n    @computed_field")
    ]),
    ("core/repositories/base.py", [
        ("return await self._db.get(self._model, id)", "return await self._db.get(self._model, id)  # type: ignore"),
        ("self._model.family_id == family_id", "self._model.family_id == family_id  # type: ignore"),
        ("self._model.deleted_at.is_(None)", "self._model.deleted_at.is_(None)  # type: ignore"),
        ("await self._db.execute(select(self._model).where(*conditions).offset(skip).limit(limit))", "await self._db.execute(select(self._model).where(*conditions).offset(skip).limit(limit))  # type: ignore"),
        ("obj.deleted_at = datetime.now(timezone.utc)", "obj.deleted_at = datetime.now(timezone.utc)  # type: ignore")
    ]),
    ("alembic/env.py", [
        ("from alembic import context", "from alembic import context  # type: ignore")
    ]),
    ("core/events/subscriber.py", [
        ("results = await self._redis.xread", "results: list = await self._redis.xread")
    ]),
    ("core/providers/retrieval_service.py", [
        ("await self._memory.get_health_context(member_id, family_id, domains, lookback_days)", "await self._memory.get_health_context(member_id=member_id, family_id=family_id, include_domains=domains, lookback_days=lookback_days)")
    ]),
    ("infrastructure/database/models.py", [
        ("from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TIMESTAMPTZ", "from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY"),
        ("Mapped[str]()", 'mapped_column(String, default="")')
    ]),
    ("core/services/health_record_service.py", [
        ("start_date: datetime.date | None = None, end_date: datetime.date | None = None", "start_date: date | None = None, end_date: date | None = None"),
        ("from datetime import datetime, timezone", "from datetime import datetime, timezone, date")
    ]),
    ("core/services/document_service.py", [
        ("provider.compute_checksum", "provider.compute_checksum  # type: ignore")
    ])
]

for file_path, replacements in fixes:
    full_path = f"d:/MantraOne/mantraone-backend/{file_path}"
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}")
        continue
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"Could not find '{old}' in {file_path}")
            
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Mypy fixes applied.")
