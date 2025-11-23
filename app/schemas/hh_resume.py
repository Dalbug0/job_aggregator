from typing import Optional

from pydantic import BaseModel

from app.examples import hh_resume


class AdditionalProperties(BaseModel):
    any_job: Optional[bool] = None


class ResumeCreate(BaseModel):
    additional_properties: Optional[AdditionalProperties] = None
    clone_resume_id: Optional[str] = None
    entry_point: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    update_profile: Optional[bool] = None
    vacancy_id: Optional[int] = None

    class Config:
        json_schema_extra = {"example": hh_resume.resume_create_example}
