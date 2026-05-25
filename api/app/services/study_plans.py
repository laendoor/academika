import uuid

from sqlalchemy import delete, insert
from sqlalchemy.exc import IntegrityError

from app.db.base import generate_uuid
from app.errors import ConflictError
from app.models.study_plan import StudyPlan, study_plan_course
from app.schemas.study_plans import StudyPlanCreate, StudyPlanUpdate
from app.services.base import BaseService


class StudyPlanService(BaseService[StudyPlan, StudyPlanCreate, StudyPlanUpdate]):
    model = StudyPlan

    async def create(self, data: StudyPlanCreate) -> StudyPlan:
        course_ids = data.course_ids
        payload = data.model_dump(exclude={"course_ids"})
        instance = StudyPlan(id=generate_uuid(), **payload)
        self.session.add(instance)
        try:
            await self.session.flush()
            await self._set_courses(instance.id, course_ids)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def update(self, id: uuid.UUID, data: StudyPlanUpdate) -> StudyPlan:
        instance = await self.get_by_id(id)
        update_data = data.model_dump(exclude_none=True, exclude={"course_ids"})
        for field, value in update_data.items():
            setattr(instance, field, value)
        try:
            if data.course_ids is not None:
                await self._set_courses(instance.id, data.course_ids)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictError(str(e.orig)) from e
        await self.session.refresh(instance)
        return instance

    async def _set_courses(self, plan_id: uuid.UUID, course_ids: list[uuid.UUID]) -> None:
        await self.session.execute(delete(study_plan_course).where(study_plan_course.c.plan_id == plan_id))
        if course_ids:
            await self.session.execute(
                insert(study_plan_course).values([{"plan_id": plan_id, "course_id": cid} for cid in course_ids])
            )
