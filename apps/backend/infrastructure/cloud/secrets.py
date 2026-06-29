import os
from config.settings import settings
import structlog

logger = structlog.get_logger()


async def get_secret(secret_name: str) -> str:
    if settings.is_development:
        env_key = f"MANTRAONE_{secret_name.upper()}"
        value = os.environ.get(env_key) or os.environ.get(secret_name.upper())
        if value is None:
            raise ValueError(f"Secret '{secret_name}' not found in environment")
        return value
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode()
    except Exception as exc:
        logger.error("secret_fetch_failed", secret_name=secret_name, error=str(exc))
        raise
