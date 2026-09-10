from typing import List, Dict, Optional, Literal
from pydantic import BaseModel

class CareerRole(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    description: str
    experienceLevel: Literal["Entry-Level", "Intermediate", "Advanced"] = "Entry-Level"
    coreSkills: List[str]
    secondarySkills: List[str]
    currentMatchPercentage: int = 0
    avgSalary: str
    demandLevel: Literal["High", "Very High", "Moderate"] = "High"
    marketInsight: str

class CareerRecommendation(BaseModel):
    career: CareerRole
    matchScore: int
    confidence: Literal["High", "Moderate", "Emerging", "Uncalibrated"]
    matchedSkills: List[str]
    missingSkills: List[str]
    interestAlignment: int
    explanation: str

class ReadinessBreakdown(BaseModel):
    skillAlignmentPoints: int # Max 450
    practicalExperiencePoints: int # Max 250
    assessmentPoints: int # Max 150
    educationPoints: int # Max 150
    totalPoints: int # Max 1000

class ReadinessResult(BaseModel):
    readinessScore: int # 0 - 100%
    readinessPoints: int # 0 - 1000
    readinessLevel: Literal["Uncalibrated", "Early Foundation", "Developing", "Proficient", "Industry Ready"]
    breakdown: ReadinessBreakdown
    statusMessage: str
    recommendationHint: str

class SkillGapItem(BaseModel):
    skill: str
    category: str
    yourLevel: int # 0 - 100
    requiredLevel: int # 0 - 100
    gap: int # max(0, requiredLevel - yourLevel)
    priority: Literal["Strong", "Developing", "Gap"]
    status: Literal["Mastered", "In Progress", "Not Started"]
    recommendation: str

class RoadmapResource(BaseModel):
    title: str
    type: str
    duration: str
    url: str
    platform: str

class PracticeProject(BaseModel):
    title: str
    description: str
    deliverable: str

class RoadmapStep(BaseModel):
    id: str
    stepNumber: str
    title: str
    status: Literal["completed", "in_progress", "upcoming"]
    whyItMatters: str
    topics: List[str]
    skillsCovered: List[str] = []
    recommendedResources: List[RoadmapResource]
    practiceProject: PracticeProject
    estimatedTime: str
    skillKey: str

class LearningResource(BaseModel):
    id: str
    title: str
    platform: Literal["YouTube", "Documentation", "Interactive", "Article"]
    level: Literal["Beginner", "Intermediate", "Advanced"]
    duration: str
    instructor: str
    url: str
    skillTag: str
    roadmapStepId: Optional[str] = None
    rating: float = 4.8
    isSaved: bool = False

class NextCareerProgression(BaseModel):
    currentCareerTitle: str
    nextCareerRole: str
    specializations: List[str]
    transferableSkills: List[str]
    skillsToAcquire: List[str]
    rationale: str

class StrongMatchItem(BaseModel):
    skill: str
    studentLevel: int
    requiredLevel: int
    note: str

class NeedsImprovementItem(BaseModel):
    skill: str
    studentLevel: int
    requiredLevel: int
    gap: int
    priority: Literal["High", "Medium", "Low"]

class BenchmarkComparisonItem(BaseModel):
    skill: str
    studentLevel: int
    benchmarkLevel: int
    category: str

class CareerMatch(BaseModel):
    careerId: str
    careerTitle: str
    overallMatch: int
    strongMatches: List[StrongMatchItem]
    needsImprovement: List[NeedsImprovementItem]
    benchmarkComparison: List[BenchmarkComparisonItem]

