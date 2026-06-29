from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

RLS_TABLES = [
    "family_members",
    "health_baselines",
    "daily_checkins",
    "watcher_signals",
    "coordinator_decisions",
    "health_metrics",
    "medications",
    "medication_logs",
    "documents",
    "diagnoses",
    "consultations",
    "escalation_events",
]


async def setup_rls_policies(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        for table in RLS_TABLES:
            await conn.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
            await conn.execute(text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))
            await conn.execute(text(f"DROP POLICY IF EXISTS {table}_family_isolation ON {table}"))
            await conn.execute(
                text(f"""
                CREATE POLICY {table}_family_isolation ON {table}
                    USING (
                        family_id = NULLIF(
                            current_setting('app.current_family_id', true), ''
                        )::UUID
                    )
            """)
            )
            logger.info("rls_policy_created", table=table)
    logger.info("rls_setup_complete", tables=RLS_TABLES)


async def set_family_context(conn, family_id: str) -> None:
    await conn.execute(text(f"SET LOCAL app.current_family_id = '{family_id}'"))
