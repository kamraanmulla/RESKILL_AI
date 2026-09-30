from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field, model_validator

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

# ==============================================================================
# Adaptive Career Intelligence Assessment Schemas
# ==============================================================================

ConfidenceLevel = Literal["guessing", "somewhat_confident", "confident", "very_confident"]
InterestRating = Literal["not_interested", "slightly_interested", "interested", "very_interested"]

class AdaptiveOptionView(BaseModel):
    id: str
    text: str

class AdaptiveQuestionView(BaseModel):
    id: str
    number: int
    totalEstimatedQuestions: int
    domain: str
    domainLabel: str
    skill: str
    difficulty: str
    questionType: str
    question: str
    scenario: Optional[str] = None
    options: List[AdaptiveOptionView]
    phase: str
    isAdaptiveFollowUp: bool = False
    contextNote: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    questionId: str
    selectedOptionId: str
    confidence: Optional[ConfidenceLevel] = "confident"

class DomainInterestItem(BaseModel):
    domain: str
    interestLevel: InterestRating

class SubmitInterestRequest(BaseModel):
    domainInterests: List[DomainInterestItem]
    scenarioPreference: Optional[str] = None

class PracticalScenarioView(BaseModel):
    id: str
    domain: str
    domainLabel: str
    title: str
    scenarioText: str
    contextSnippet: Optional[str] = None
    options: List[AdaptiveOptionView]

class SubmitPracticalRequest(BaseModel):
    scenarioId: str
    selectedOptionId: str
    reasoning: Optional[str] = ""

class DomainKnowledgeSignal(BaseModel):
    domain: str
    domainLabel: str
    demonstratedKnowledge: int
    evidenceCount: int
    skillsDemonstrated: List[str] = []
    confidenceSignal: str
    practicalScore: int
    interestLevel: str
    evidenceStrength: str
    uncertainty: str

class CareerPathwayResult(BaseModel):
    careerId: str
    title: str
    category: str
    matchScore: int
    knowledgeAlignment: str
    interestLevel: str
    practicalEvidence: str
    existingSkills: List[str] = []
    transferableSkills: List[str] = []
    missingSkills: List[str] = []
    requiredSkills: List[str] = []
    explanation: str

class DiscoveredCombinationResult(BaseModel):
    career: str
    combination: List[str]
    confidence: float
    supportingSkills: List[str]
    missingSkills: List[str]
    explanation: str

class CareerIntelligenceProfile(BaseModel):
    userId: str = "std_guest"
    completedAt: str
    totalQuestionsAnswered: int
    isMultiDomain: bool = False
    profileObservation: str
    breadthVsDepth: str
    theoryVsPractical: str
    domainSignals: Dict[str, DomainKnowledgeSignal]
    discoveredCombinations: List[DiscoveredCombinationResult] = []
    relevantPathways: List[CareerPathwayResult] = []
    suggestedNextDevelopment: List[str] = []

class AssessmentSessionState(BaseModel):
    sessionId: str
    userId: str
    currentPhase: str  # "MIXED_DISCOVERY", "ADAPTIVE_EXPLORATION", "INTEREST_DISCOVERY", "PRACTICAL_CHALLENGE", "COMPLETED"
    questionNumber: int
    totalEstimatedQuestions: int
    questionsAnsweredCount: int
    currentQuestion: Optional[AdaptiveQuestionView] = None
    currentPracticalScenario: Optional[PracticalScenarioView] = None
    isComplete: bool = False
    preliminarySignals: Optional[Dict[str, int]] = None
    profile: Optional[CareerIntelligenceProfile] = None

