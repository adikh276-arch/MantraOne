import structlog
from config.settings import settings

logger = structlog.get_logger()

async def verify_firebase_token(token: str) -> dict:
    if settings.firebase_mock_enabled:
        if token.startswith("test-token-"):
            uid = token.removeprefix("test-token-")
            if not uid:
                raise ValueError("Invalid mock token: uid cannot be empty")
            return {"uid": uid, "email": f"{uid}@test.local", "email_verified": True}
        raise ValueError("Invalid mock token format. Expected: test-token-{uid}")
    
    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        return firebase_auth.verify_id_token(token)
    except Exception as exc:
        logger.warning("firebase_token_verification_failed", error=str(exc))
        raise ValueError(f"Token verification failed: {exc}") from exc
