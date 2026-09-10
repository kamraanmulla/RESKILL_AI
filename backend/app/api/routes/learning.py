from fastapi import APIRouter
from typing import List, Optional
from ...schemas.intelligence import LearningResource
from ...intelligence.skill_gap_engine import SkillGapEngine
from .profile_store import get_profile

router = APIRouter(prefix="/learning", tags=["Learning Resources"])

# Verified catalog of video learning resources with specific YouTube watch URLs
_resources_db: List[LearningResource] = [
    LearningResource(
        id="res_01",
        title="Node.js Full Course for Beginners | Complete All-in-One Tutorial",
        platform="YouTube",
        level="Intermediate",
        duration="7h 00m",
        instructor="Dave Gray",
        url="https://www.youtube.com/watch?v=f2EqECiTBL8",
        skillTag="Node.js"
    ),
    LearningResource(
        id="res_02",
        title="What Is REST API? Examples And How To Use It",
        platform="YouTube",
        level="Beginner",
        duration="15m",
        instructor="ByteByteGo",
        url="https://www.youtube.com/watch?v=-mN3VyJuCjM",
        skillTag="REST APIs"
    ),
    LearningResource(
        id="res_03",
        title="Linux Crash Course for Beginners with Labs",
        platform="YouTube",
        level="Beginner",
        duration="2h 15m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=6WatcfENsOU",
        skillTag="Linux"
    ),
    LearningResource(
        id="res_04",
        title="Computer Networking Full Course - OSI Model Deep Dive with Real Life Examples",
        platform="YouTube",
        level="Intermediate",
        duration="4h 30m",
        instructor="Kunal Kushwaha",
        url="https://www.youtube.com/watch?v=IPvYjXCsTg8",
        skillTag="Networking"
    ),
    LearningResource(
        id="res_05",
        title="Wazuh SIEM Complete Beginner's Guide | Concepts, Installation & Setup",
        platform="YouTube",
        level="Intermediate",
        duration="1h 45m",
        instructor="Tech on Target",
        url="https://www.youtube.com/watch?v=mKijuwrTeRM",
        skillTag="SIEM"
    ),
    LearningResource(
        id="res_06",
        title="Learn Python – Interactive Course 2026",
        platform="YouTube",
        level="Beginner",
        duration="4h 20m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=kLZgQWjnUz0",
        skillTag="Python"
    ),
    LearningResource(
        id="res_07",
        title="JavaScript Crash Course For Beginners",
        platform="YouTube",
        level="Beginner",
        duration="1h 40m",
        instructor="Traversy Media",
        url="https://www.youtube.com/watch?v=hdI2bqOjy3c",
        skillTag="JavaScript"
    ),
    LearningResource(
        id="res_08",
        title="React Crash Course for Modern Web Apps",
        platform="YouTube",
        level="Intermediate",
        duration="2h 15m",
        instructor="Traversy Media",
        url="https://www.youtube.com/watch?v=LDB4uaJ87e0",
        skillTag="React"
    ),
    LearningResource(
        id="res_09",
        title="TypeScript Tutorial for Beginners",
        platform="YouTube",
        level="Intermediate",
        duration="1h 00m",
        instructor="Programming with Mosh",
        url="https://www.youtube.com/watch?v=d56mG7DezGs",
        skillTag="TypeScript"
    ),
    LearningResource(
        id="res_10",
        title="HTML Tutorial for Beginners: HTML Crash Course",
        platform="YouTube",
        level="Beginner",
        duration="1h 10m",
        instructor="Programming with Mosh",
        url="https://www.youtube.com/watch?v=qz0aGYrrlhU",
        skillTag="HTML/CSS"
    ),
    LearningResource(
        id="res_11",
        title="Learn Express JS In 35 Minutes",
        platform="YouTube",
        level="Intermediate",
        duration="35m",
        instructor="Web Dev Simplified",
        url="https://www.youtube.com/watch?v=SccSCuHhOw0",
        skillTag="Express"
    ),
    LearningResource(
        id="res_12",
        title="SQL Tutorial - Full Database Course for Beginners",
        platform="YouTube",
        level="Beginner",
        duration="4h 20m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=HXV3zeQKqGY",
        skillTag="SQL"
    ),
    LearningResource(
        id="res_13",
        title="MongoDB Crash Course",
        platform="YouTube",
        level="Intermediate",
        duration="30m",
        instructor="Web Dev Simplified",
        url="https://www.youtube.com/watch?v=ofme2o29ngU",
        skillTag="MongoDB"
    ),
    LearningResource(
        id="res_14",
        title="Cyber Security Full Course 2026 | Beginner to Advanced Course",
        platform="YouTube",
        level="Beginner",
        duration="6h 00m",
        instructor="Simplilearn",
        url="https://www.youtube.com/watch?v=IjbSt71piWQ",
        skillTag="Cybersecurity"
    ),
    LearningResource(
        id="res_15",
        title="Incident Response Process - SY0-601 CompTIA Security+",
        platform="YouTube",
        level="Intermediate",
        duration="45m",
        instructor="Professor Messer",
        url="https://www.youtube.com/watch?v=fU_w8Ou9RVg",
        skillTag="Incident Response"
    ),
    LearningResource(
        id="res_16",
        title="Docker Tutorial for Beginners [FULL COURSE in 3 Hours]",
        platform="YouTube",
        level="Beginner",
        duration="3h 05m",
        instructor="TechWorld with Nana",
        url="https://www.youtube.com/watch?v=3c-iBn73dDE",
        skillTag="Docker"
    ),
    LearningResource(
        id="res_17",
        title="Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours]",
        platform="YouTube",
        level="Intermediate",
        duration="3h 50m",
        instructor="TechWorld with Nana",
        url="https://www.youtube.com/watch?v=X48VuDVv0do",
        skillTag="Kubernetes"
    ),
    LearningResource(
        id="res_18",
        title="Git & GitHub Crash Course for Beginners",
        platform="YouTube",
        level="Beginner",
        duration="1h 15m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=mAFoROnOfHs",
        skillTag="Git"
    ),
    LearningResource(
        id="res_19",
        title="Machine Learning for Everybody – Full Course",
        platform="YouTube",
        level="Intermediate",
        duration="3h 50m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=i_LwzRVP7bg",
        skillTag="Machine Learning"
    ),
    LearningResource(
        id="res_20",
        title="Data Analysis with Python: Complete Live Course",
        platform="YouTube",
        level="Intermediate",
        duration="4h 15m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=EsDFiZPljYo",
        skillTag="Data Analysis"
    ),
    LearningResource(
        id="res_21",
        title="Complete Python Pandas Data Science Tutorial",
        platform="YouTube",
        level="Beginner",
        duration="1h 00m",
        instructor="Keith Galli",
        url="https://www.youtube.com/watch?v=2uvysYbKdjM",
        skillTag="Pandas"
    ),
    LearningResource(
        id="res_22",
        title="AWS Tutorial For Beginners | AWS Full Course in 10 Hours",
        platform="YouTube",
        level="Beginner",
        duration="10h 00m",
        instructor="edureka!",
        url="https://www.youtube.com/watch?v=k1RI5locZE4",
        skillTag="Cloud"
    ),
    LearningResource(
        id="res_23",
        title="Statistics - A Full University Course on Data Science Basics",
        platform="YouTube",
        level="Beginner",
        duration="8h 15m",
        instructor="freeCodeCamp.org",
        url="https://www.youtube.com/watch?v=xxpc-HPKN28",
        skillTag="Statistics"
    )
]

@router.get("", response_model=List[LearningResource])
def get_learning_resources(skill: Optional[str] = None):
    profile = get_profile()
    if skill and skill != "All":
        return [r for r in _resources_db if r.skillTag.lower() == skill.lower()]

    # Prioritize resources addressing active skill gaps
    gaps = SkillGapEngine.calculate_skill_gaps(profile)
    gap_names = [g.skill.lower() for g in gaps if g.priority in ["Gap", "Developing"]]

    if gap_names:
        matched_resources = [r for r in _resources_db if any(gn in r.skillTag.lower() or r.skillTag.lower() in gn for gn in gap_names)]
        other_resources = [r for r in _resources_db if r not in matched_resources]
        return matched_resources + other_resources

    return _resources_db

@router.post("/{res_id}/toggle-save", response_model=List[LearningResource])
def toggle_save_resource(res_id: str):
    for r in _resources_db:
        if r.id == res_id:
            r.isSaved = not r.isSaved
            break
    return _resources_db
