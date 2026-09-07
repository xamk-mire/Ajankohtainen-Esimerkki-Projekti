"""SQLAdmin at /admin. Register a ModelView here when you add an ORM model."""

import secrets

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import get_settings
from app.db.session import engine
from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.unit_type import UnitType
from app.models.user import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username") or "")
        password = str(form.get("password") or "")
        settings = get_settings()
        username_ok = secrets.compare_digest(username, settings.sqladmin_username)
        password_ok = secrets.compare_digest(password, settings.sqladmin_password)
        if username_ok and password_ok:
            request.session.update({"token": "sqladmin"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("token"))


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.display_name, User.created_at]
    column_details_exclude_list = [User.password_hash]
    form_excluded_columns = [User.password_hash]
    column_searchable_list = [User.email, User.display_name]
    column_sortable_list = [User.email, User.display_name, User.created_at]


class ActivityTypeAdmin(ModelView, model=ActivityType):
    name_plural = "Activity types"
    column_list = [
        ActivityType.name,
        ActivityType.slug,
        ActivityType.is_system,
        ActivityType.user_id,
    ]
    column_searchable_list = [ActivityType.name, ActivityType.slug]
    column_sortable_list = [ActivityType.name, ActivityType.slug, ActivityType.is_system]


class UnitTypeAdmin(ModelView, model=UnitType):
    name_plural = "Unit types"
    column_list = [
        UnitType.name,
        UnitType.slug,
        UnitType.unit_label,
        UnitType.is_system,
    ]
    column_searchable_list = [UnitType.name, UnitType.slug]
    column_sortable_list = [UnitType.name, UnitType.slug]


class ActivityTypeUnitTypeAdmin(ModelView, model=ActivityTypeUnitType):
    name = "Activity unit link"
    name_plural = "Activity unit links"
    column_list = [
        ActivityTypeUnitType.activity_type,
        ActivityTypeUnitType.unit_type,
        ActivityTypeUnitType.sort_order,
        ActivityTypeUnitType.is_required,
        ActivityTypeUnitType.per_set,
    ]
    column_sortable_list = [
        ActivityTypeUnitType.sort_order,
        ActivityTypeUnitType.per_set,
    ]


def setup_admin(app: FastAPI) -> None:
    settings = get_settings()
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=settings.sqladmin_secret_key),
        title="Exercise Tracker Admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(ActivityTypeAdmin)
    admin.add_view(UnitTypeAdmin)
    admin.add_view(ActivityTypeUnitTypeAdmin)
