import os

fixes = [
    ("alembic/env.py", [
        ("from infrastructure.database import models", "")
    ]),
    ("api/dependencies.py", [
        ("from typing import AsyncGenerator, Annotated", "from typing import AsyncGenerator")
    ]),
    ("api/main.py", [
        ("from fastapi import FastAPI, Depends", "from fastapi import FastAPI")
    ]),
    ("core/domain/entities.py", [
        ("from dataclasses import dataclass, field", "from dataclasses import dataclass"),
        ("SelectionReason, MemoryOperationType,", "SelectionReason,")
    ]),
    ("core/events/publisher.py", [
        ("import json\n", ""),
        ("from infrastructure.cache.redis_client import STREAM_NAME, publish_event", "from infrastructure.cache.redis_client import publish_event")
    ]),
    ("core/providers/encryption_service.py", [
        ("if not plaintext: return plaintext", "if not plaintext:\n            return plaintext"),
        ("if not ciphertext: return ciphertext", "if not ciphertext:\n            return ciphertext"),
        ("if not ciphertext: return {}", "if not ciphertext:\n            return {}")
    ]),
    ("core/providers/llm_provider.py", [
        ('if start == -1 or end == 0: raise ValueError(f"Invalid JSON: {text[:200]}")', 'if start == -1 or end == 0:\n            raise ValueError(f"Invalid JSON: {text[:200]}")')
    ]),
    ("core/providers/memory_provider.py", [
        ("from cognee.api.v1.search import SearchType\n", ""),
        ("from datetime import datetime, timezone", "from datetime import datetime"),
        ("from core.domain.enums import MemoryType, MemoryOperationType\n", ""),
        ("if self._configured: return", "if self._configured:\n            return")
    ]),
    ("core/repositories/base.py", [
        ("from sqlalchemy import select, update", "from sqlalchemy import select")
    ]),
    ("core/repositories/checkin_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", ""),
        ("DailyCheckin.memory_ingested == False", "DailyCheckin.memory_ingested.is_(False)")
    ]),
    ("core/repositories/coordinator_decision_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", "")
    ]),
    ("core/repositories/document_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", "")
    ]),
    ("core/repositories/escalation_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", "")
    ]),
    ("core/repositories/health_record_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", ""),
        ("if start_date: conditions.append(HealthMetric.recorded_at >= start_date)", "if start_date:\n            conditions.append(HealthMetric.recorded_at >= start_date)"),
        ("if end_date: conditions.append(HealthMetric.recorded_at <= end_date)", "if end_date:\n            conditions.append(HealthMetric.recorded_at <= end_date)"),
        ("Medication.is_active == True", "Medication.is_active.is_(True)")
    ]),
    ("core/repositories/member_repository.py", [
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", ""),
        ("if family_id: conditions.append(FamilyMember.family_id == family_id)", "if family_id:\n            conditions.append(FamilyMember.family_id == family_id)"),
        ("FamilyMember.is_primary == True", "FamilyMember.is_primary.is_(True)")
    ]),
    ("core/repositories/watcher_signal_repository.py", [
        ("from datetime import datetime, timedelta, timezone, date", "from datetime import datetime, timedelta, timezone"),
        ("from sqlalchemy.ext.asyncio import AsyncSession\n", ""),
        ("WatcherSignal.surfaced == False", "WatcherSignal.surfaced.is_(False)")
    ]),
    ("core/services/checkin_service.py", [
        ("from datetime import date\n", "")
    ]),
    ("core/services/coordinator_service.py", [
        ("from core.domain.enums import WatcherDomain\n", ""),
        ("from datetime import datetime, timezone\n", "")
    ]),
    ("core/workers/narrative_builder.py", [
        ("from uuid import UUID\n", "")
    ]),
    ("core/workers/watchers/base_watcher.py", [
        ("from typing import Any\n", "")
    ]),
    ("core/workers/worker_main.py", [
        ("from redis.asyncio import Redis, ConnectionPool", "from redis.asyncio import Redis")
    ]),
    ("infrastructure/cloud/storage.py", [
        ("import aiofiles\n", ""),
        ("import hashlib\n", ""),
        ("import json\n", ""),
        ("import secrets\n", ""),
        ("import time\n", "")
    ]),
    ("infrastructure/database/models.py", [
        ("String, Boolean, Integer, Float, Text, Date, DateTime,", "String, Boolean, Integer, Float, Text, Date,")
    ]),
    ("scripts/ponytail_check.py", [
        ("import os\n", ""),
        ("if not pattern: continue", "if not pattern:\n            continue"),
        ('if not pyfile.exists() or pyfile.is_dir() or str(pyfile).startswith("venv") or str(pyfile).startswith(".venv"): continue', 'if not pyfile.exists() or pyfile.is_dir() or str(pyfile).startswith("venv") or str(pyfile).startswith(".venv"):\n                continue')
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

print("Fixes applied.")
