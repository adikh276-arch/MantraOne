from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass
class PermissionContext:
    actor_id: UUID
    actor_role: str
    target_id: UUID
    target_role: str
    target_relationship: str
    resource_type: str
    resource_id: Optional[str]
    scope: str
    explicit_grants: List[dict] # list of active grants matching target
    is_document_owner: bool = False

@dataclass
class PermissionResult:
    is_allowed: bool
    reason: str

class PolicyEngine:
    """
    Evaluates fine-grained permissions for accessing family resources based on roles,
    relationships, explicit grants, resource scopes, and data ownership.
    """
    
    SENSITIVE_SCOPES = {"mental_health", "reproductive_health"}

    def evaluate(self, ctx: PermissionContext) -> PermissionResult:
        # 1. Self Access
        if ctx.actor_id == ctx.target_id:
            return PermissionResult(True, "Self access granted")

        # 2. Document Owner Access
        if ctx.resource_type == "document" and ctx.is_document_owner:
            return PermissionResult(True, "Document owner access granted")

        # 3. Explicit Grants Evaluation (Highest Priority over defaults)
        valid_grants = [
            g for g in ctx.explicit_grants 
            if g['scope'] in {ctx.scope, 'all_health', '*'} and
            (g['expires_at'] is None or g['expires_at'] > datetime.now(timezone.utc))
        ]
        if valid_grants:
            return PermissionResult(True, "Explicit grant access")

        # 4. Caregiver (Must have explicit grant for access, handled above)
        if ctx.actor_role == "caregiver":
            return PermissionResult(False, "Caregiver requires explicit grant")

        # 5. Sensitive Domains (Mental Health, Reproductive Health)
        # Without an explicit grant, NO ONE can access sensitive domains for another member
        if ctx.scope in self.SENSITIVE_SCOPES:
            return PermissionResult(False, "Sensitive domains require explicit grant")

        # 6. Minor access (Parents/Owners can typically see minor's non-sensitive data)
        # If target is minor, and actor is owner/admin, allow. 
        # (Assuming the primary relationship is parent/child for simplicity in this engine)
        if ctx.target_role == "minor" and ctx.actor_role in {"owner", "admin"}:
            return PermissionResult(True, "Parental/Guardian access to minor")

        # 7. Owner/Admin access to non-sensitive data
        if ctx.actor_role in {"owner", "admin"}:
            return PermissionResult(True, "Owner/Admin access to standard domain")

        # Default Deny
        return PermissionResult(False, "No applicable policy allows access")
