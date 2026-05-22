"""Multi-tenant authentication and RBAC"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Role(str, Enum):
    FARM_OWNER = "farm_owner"
    AGRONOMIST = "agronomist"
    TECHNICIAN = "technician"
    DATA_SCIENTIST = "data_scientist"
    ADMIN = "admin"


class Permission(str, Enum):
    VIEW_FARM = "view_farm"
    EDIT_FARM = "edit_farm"
    DELETE_FARM = "delete_farm"
    MANAGE_ROBOTS = "manage_robots"
    INSTALL_PLUGINS = "install_plugins"
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    CONFIGURE_ALERTS = "configure_alerts"


class EnterpriseAuth:
    """Multi-tenant authentication and RBAC"""

    def __init__(self):
        self.users = {}
        self.organizations = {}
        self.role_permissions = {
            Role.FARM_OWNER: [
                Permission.VIEW_FARM,
                Permission.EDIT_FARM,
                Permission.MANAGE_ROBOTS,
                Permission.MANAGE_USERS,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.CONFIGURE_ALERTS,
            ],
            Role.AGRONOMIST: [
                Permission.VIEW_FARM,
                Permission.EDIT_FARM,
                Permission.MANAGE_ROBOTS,
                Permission.VIEW_ANALYTICS,
                Permission.CONFIGURE_ALERTS,
            ],
            Role.TECHNICIAN: [
                Permission.VIEW_FARM,
                Permission.MANAGE_ROBOTS,
                Permission.VIEW_ANALYTICS,
            ],
            Role.DATA_SCIENTIST: [
                Permission.VIEW_FARM,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
            ],
            Role.ADMIN: list(Permission),
        }

    async def create_organization(
        self,
        org_id: str,
        name: str,
        owner_email: str,
    ) -> Dict[str, Any]:
        """Create enterprise organization"""
        logger.info(f"Creating organization {org_id}")

        self.organizations[org_id] = {
            "id": org_id,
            "name": name,
            "owner_email": owner_email,
            "created_at": datetime.utcnow().isoformat(),
            "subscription_tier": "enterprise",
            "num_farms": 0,
            "num_users": 0,
            "api_key": f"sk_{org_id}_{int(datetime.utcnow().timestamp())}",
        }

        return self.organizations[org_id]

    async def add_user_to_organization(
        self,
        org_id: str,
        user_email: str,
        role: Role,
    ) -> Dict[str, Any]:
        """Add user to organization with role"""
        if org_id not in self.organizations:
            return {"error": f"Organization {org_id} not found"}

        user_id = f"user_{user_email.replace('@', '_')}"
        self.users[user_id] = {
            "id": user_id,
            "email": user_email,
            "organization_id": org_id,
            "role": role,
            "permissions": self.role_permissions[role],
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
        }

        self.organizations[org_id]["num_users"] += 1
        logger.info(f"User {user_email} added to {org_id} as {role}")

        return self.users[user_id]

    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
    ) -> bool:
        """Check if user has permission"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        return permission in user["permissions"]

    async def get_user_farms(self, user_id: str) -> List[str]:
        """Get farms accessible to user"""
        if user_id not in self.users:
            return []

        return []

    async def revoke_access(self, user_id: str, org_id: str) -> bool:
        """Revoke user access to organization"""
        if user_id in self.users:
            del self.users[user_id]
        logger.info(f"Access revoked for {user_id} from {org_id}")
        return True
