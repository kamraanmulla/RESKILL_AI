from typing import List, Dict, Optional
from pydantic import BaseModel, model_validator

class AssessmentOption(BaseModel):
    id: str
    text: str
    domainSignal: str # e.g. "cybersecurity", "software_engineering", "data_science", "ai_ml", "cloud_devops"
    traitSignal: str  # e.g. "investigative", "builder", "analytical", "experimental", "systems"
    styleSignal: Optional[str] = None

    @model_validator(mode="after")
    def populate_style_signal(self):
        if not self.styleSignal:
            self.styleSignal = self.traitSignal
        return self

class AssessmentQuestion(BaseModel):
    id: str
    number: int
    title: str
    subtitle: str
    question: Optional[str] = None
    subtext: Optional[str] = None
    options: List[AssessmentOption]

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.question:
            self.question = self.title
        if not self.subtext:
            self.subtext = self.subtitle
        return self

class AssessmentSubmission(BaseModel):
    answers: Dict[str, str] # question_id -> option_id

class AssessmentEvaluationResult(BaseModel):
    domainPreferences: List[str]
    problemSolvingStyle: str
    workStyleSignals: List[str]
    primaryMotivation: str
    careerInterestScores: Dict[str, int]
