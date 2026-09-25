"""SQLAdmin at ``/admin``. Login is env-based (``SQLADMIN_*``), not JWT.

Checklist when you add an ORM model:

1. Import the model and add a ``ModelView`` subclass below.
2. Register it with ``admin.add_view(...)`` in ``setup_admin``.
3. Keep secrets out of list, detail, form, and export columns
   (``password_hash``, future tokens, and similar).

Sprint 3 sessions, items, measurements, plans, and goals are registered.
A new model still needs its own view.
"""

import secrets

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import get_settings
from app.db.session import engine
from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.goal import Goal
from app.models.unit_type import UnitType
from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem
from app.models.workout_session_measurement import WorkoutSessionMeasurement


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


# A new ORM model needs a new ModelView here, then admin.add_view in setup_admin.
# List foreign-key ids, not relationship collections, so the list page stays a table.


class WorkoutSessionAdmin(ModelView, model=WorkoutSession):
    name = "Session"
    name_plural = "Sessions"
    icon = "fa-solid fa-dumbbell"
    category = "Training log"
    column_list = [
        WorkoutSession.name,
        WorkoutSession.user_id,
        WorkoutSession.session_at,
        WorkoutSession.status,
        WorkoutSession.plan_id,
    ]
    column_searchable_list = [WorkoutSession.name, WorkoutSession.status]
    column_sortable_list = [
        WorkoutSession.name,
        WorkoutSession.session_at,
        WorkoutSession.status,
    ]
    form_columns = [
        WorkoutSession.user_id,
        WorkoutSession.name,
        WorkoutSession.session_at,
        WorkoutSession.status,
        WorkoutSession.notes,
        WorkoutSession.intensity,
        WorkoutSession.plan_id,
        WorkoutSession.source_session_id,
    ]


class WorkoutSessionItemAdmin(ModelView, model=WorkoutSessionItem):
    name = "Session exercise"
    name_plural = "Session exercises"
    icon = "fa-solid fa-list"
    category = "Training log"
    column_list = [
        WorkoutSessionItem.session_id,
        WorkoutSessionItem.activity_type_id,
        WorkoutSessionItem.sort_order,
        WorkoutSessionItem.notes,
    ]
    column_sortable_list = [WorkoutSessionItem.sort_order]
    form_columns = [
        WorkoutSessionItem.session_id,
        WorkoutSessionItem.activity_type_id,
        WorkoutSessionItem.sort_order,
        WorkoutSessionItem.notes,
    ]


class WorkoutSessionMeasurementAdmin(ModelView, model=WorkoutSessionMeasurement):
    name = "Measurement"
    name_plural = "Measurements"
    icon = "fa-solid fa-ruler"
    category = "Training log"
    column_list = [
        WorkoutSessionMeasurement.session_item_id,
        WorkoutSessionMeasurement.unit_type_id,
        WorkoutSessionMeasurement.planned_value,
        WorkoutSessionMeasurement.actual_value,
        WorkoutSessionMeasurement.set_index,
    ]
    column_sortable_list = [WorkoutSessionMeasurement.set_index]
    form_columns = [
        WorkoutSessionMeasurement.session_item_id,
        WorkoutSessionMeasurement.unit_type_id,
        WorkoutSessionMeasurement.planned_value,
        WorkoutSessionMeasurement.actual_value,
        WorkoutSessionMeasurement.set_index,
    ]


class WorkoutPlanAdmin(ModelView, model=WorkoutPlan):
    name = "Plan"
    name_plural = "Plans"
    icon = "fa-solid fa-clipboard"
    category = "Training log"
    column_list = [
        WorkoutPlan.name,
        WorkoutPlan.user_id,
        WorkoutPlan.start_date,
        WorkoutPlan.length_weeks,
    ]
    column_searchable_list = [WorkoutPlan.name]
    column_sortable_list = [WorkoutPlan.name, WorkoutPlan.start_date]
    form_columns = [
        WorkoutPlan.user_id,
        WorkoutPlan.name,
        WorkoutPlan.notes,
        WorkoutPlan.start_date,
        WorkoutPlan.length_weeks,
    ]


class GoalAdmin(ModelView, model=Goal):
    name = "Period goal"
    name_plural = "Period goals"
    icon = "fa-solid fa-bullseye"
    category = "Training log"
    column_list = [
        Goal.user_id,
        Goal.unit_type_id,
        Goal.activity_type_id,
        Goal.target_value,
        Goal.period,
        Goal.active,
    ]
    column_searchable_list = [Goal.period]
    column_sortable_list = [Goal.period, Goal.target_value, Goal.active]
    form_columns = [
        Goal.user_id,
        Goal.unit_type_id,
        Goal.activity_type_id,
        Goal.target_value,
        Goal.period,
        Goal.active,
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
    admin.add_view(WorkoutSessionAdmin)
    admin.add_view(WorkoutSessionItemAdmin)
    admin.add_view(WorkoutSessionMeasurementAdmin)
    admin.add_view(WorkoutPlanAdmin)
    admin.add_view(GoalAdmin)
