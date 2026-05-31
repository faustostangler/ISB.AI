import logging

from prometheus_client import Counter

from isb.shared_kernel.ports.authorization import Action, AuthorizationPort, Resource, Subject

# Configure security audit logging
logger = logging.getLogger("isb.security")

# Prometheus Counter for tracking access control failures (Golden Signals: Errors)
AUTH_DENIALS_COUNTER = Counter(
    "isb_auth_denials_total",
    "Total number of authorization check denials",
    ["resource_type", "action"],
)


class LocalRuleAuthorizationAdapter(AuthorizationPort):
    """Adapter executing local rule-based attribute evaluation for authorization."""

    def __init__(self) -> None:
        """Initializes the adapter."""
        pass

    def authorize(self, subject: Subject, action: Action, resource: Resource) -> bool:
        """Evaluates access control rules locally.

        Args:
            subject: The requesting subject.
            action: The requested action.
            resource: The target resource.

        Returns:
            bool: True if authorized, False otherwise.
        """
        # 1. Subject validation: reject immediately if user_id is invalid or empty
        if not subject.user_id or not subject.user_id.strip():  # pragma: no mutate
            logger.warning(  # pragma: no mutate
                "Access Denied: Subject has an empty or invalid user ID. Action=%s, ResourceId=%s",  # pragma: no mutate
                action.value,  # pragma: no mutate
                resource.resource_id,  # pragma: no mutate
            )  # pragma: no mutate
            AUTH_DENIALS_COUNTER.labels(  # pragma: no mutate
                resource_type=resource.resource_type,  # pragma: no mutate
                action=action.value,  # pragma: no mutate
            ).inc()  # pragma: no mutate
            return False

        # 2. Admin bypass check: check if user holds the administrator role
        if subject.claims.get("role") == "administrator":
            return True

        # 3. Ownership match check: check if the user matches the resource owner
        if resource.owner_id == subject.user_id:
            return True

        # 4. Access Denied: emit audit warning log and increment prometheus metrics
        logger.warning(  # pragma: no mutate
            "Access Denied: Subject is not authorized. "  # pragma: no mutate
            "UserId=%s, Action=%s, ResourceId=%s, ResourceType=%s",  # pragma: no mutate
            subject.user_id,  # pragma: no mutate
            action.value,  # pragma: no mutate
            resource.resource_id,  # pragma: no mutate
            resource.resource_type,  # pragma: no mutate
        )  # pragma: no mutate
        AUTH_DENIALS_COUNTER.labels(  # pragma: no mutate
            resource_type=resource.resource_type,  # pragma: no mutate
            action=action.value,  # pragma: no mutate
        ).inc()  # pragma: no mutate

        return False
