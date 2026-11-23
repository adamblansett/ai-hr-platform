from backend.app.api.deps import (
    get_db,
    get_current_user,
    require_role,
    security,
)

# Alias require_roles to require_role for backwards compatibility
require_roles = require_role

__all__ = [
    "get_db",
    "get_current_user",
    "require_role",
    "require_roles",
    "security",
]
