from typing import Any, Literal
from pydantic import BaseModel, Field

EventType = Literal['fatigue', 'hungry', 'crowd', 'leave_early', 'stay_longer', 'animal_active', 'off_route', 'weather_change']

class Preferences(BaseModel):
    duration_minutes: int = Field(120, ge=30, le=720)
    pace: Literal['slow', 'balanced', 'challenge'] = 'slow'
    avoid_climbing: bool = True
    avoid_sun: bool = True
    with_child: bool = True
    preferred_animals: list[str] = []
    must_visit: list[str] = []
    avoid_pois: list[str] = []
    stroller: bool = False
    wheelchair: bool = False
    start_poi: str = 'north_gate'
    end_poi: str = 'north_gate'

class RoutePlanRequest(BaseModel):
    natural_language: str = ''
    preferences: Preferences = Preferences()

class ReplanRequest(BaseModel):
    session_id: str
    reason: str = ''
    keep_pois: list[str] = []

class StartSessionRequest(BaseModel):
    route_id: str

class SessionEventRequest(BaseModel):
    session_id: str
    event_type: EventType
    value: Any = None
    note: str = ''

