from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl

class JobOpportunity(BaseModel):
    id: str
    title: str
    company: str
    location: str
    workMode: Literal["Remote", "Hybrid", "On-site"]
    type: Literal["Full-time", "Internship", "Contract"]
    matchPercentage: int
    matchedSkills: List[str]
    missingSkills: List[str]
    compensation: str
    postedAgo: str
    isSaved: bool = False
    isDemoSample: bool = False
    source: Literal["LinkedIn", "Company Website", "Campus Placement Portal"] = "LinkedIn"
    sourceUrl: str
    description: str
    responsibilities: List[str]
    qualifications: List[str]
    applyClicked: bool = False
