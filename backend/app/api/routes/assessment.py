from fastapi import APIRouter
from typing import List, Dict
from ...schemas.assessment import AssessmentQuestion, AssessmentOption, AssessmentSubmission, AssessmentEvaluationResult
from ...schemas.profile import AssessmentSignals, StudentProfile
from .profile_store import get_profile, set_profile

router = APIRouter(prefix="/assessment", tags=["Career Assessment"])

ASSESSMENT_QUESTIONS: List[AssessmentQuestion] = [
    AssessmentQuestion(
        id="q1",
        number=1,
        title="Which type of problem would you enjoy solving most?",
        subtitle="Identifies your core technical problem domain attraction.",
        options=[
            AssessmentOption(id="q1_sec", text="Finding security threats and investigating breach incidents", domainSignal="cybersecurity", traitSignal="investigative"),
            AssessmentOption(id="q1_sw", text="Building web applications and interactive client features", domainSignal="software_engineering", traitSignal="builder"),
            AssessmentOption(id="q1_data", text="Understanding datasets, trends, and business metrics", domainSignal="data_science", traitSignal="analytical"),
            AssessmentOption(id="q1_ai", text="Designing intelligent models, prompts, and inference pipelines", domainSignal="ai_ml", traitSignal="experimental"),
            AssessmentOption(id="q1_cloud", text="Managing server infrastructure, containers, and cloud networks", domainSignal="cloud_devops", traitSignal="systems")
        ]
    ),
    AssessmentQuestion(
        id="q2",
        number=2,
        title="When something doesn't work, what sounds most interesting to you?",
        subtitle="Identifies your diagnostic vs generative problem-solving preference.",
        options=[
            AssessmentOption(id="q2_inv", text="Investigating system logs and tracing the failure root cause", domainSignal="cybersecurity", traitSignal="diagnostic"),
            AssessmentOption(id="q2_fix", text="Refactoring the code and architecting a cleaner implementation", domainSignal="software_engineering", traitSignal="craftsmanship"),
            AssessmentOption(id="q2_ana", text="Analyzing transaction data and statistical patterns behind the drop", domainSignal="data_science", traitSignal="analytical"),
            AssessmentOption(id="q2_exp", text="Experimenting with multiple alternative model configurations", domainSignal="ai_ml", traitSignal="experimental"),
            AssessmentOption(id="q2_arch", text="Redesigning system resilience, network failover, and redundancy", domainSignal="cloud_devops", traitSignal="systems")
        ]
    ),
    AssessmentQuestion(
        id="q3",
        number=3,
        title="What kind of work would keep you energized over the long run?",
        subtitle="Reveals your sustained engagement style in engineering teams.",
        options=[
            AssessmentOption(id="q3_sec", text="Protecting systems, auditing attack surfaces, and finding vulnerabilities", domainSignal="cybersecurity", traitSignal="adversarial_defense"),
            AssessmentOption(id="q3_prod", text="Shipping real products used daily by end-users", domainSignal="software_engineering", traitSignal="product_impact"),
            AssessmentOption(id="q3_res", text="Conducting quantitative research and extracting insights from massive data", domainSignal="data_science", traitSignal="research"),
            AssessmentOption(id="q3_ai", text="Building intelligent systems that learn and adapt from feedback", domainSignal="ai_ml", traitSignal="innovation"),
            AssessmentOption(id="q3_sys", text="Automating deployments, cloud infrastructure, and 99.99% uptime", domainSignal="cloud_devops", traitSignal="reliability")
        ]
    ),
    AssessmentQuestion(
        id="q4",
        number=4,
        title="What matters most to you in your first career trajectory?",
        subtitle="Identifies your primary outcome motivation.",
        options=[
            AssessmentOption(id="q4_sec", text="High-demand diagnostic rigor in defensive security operations", domainSignal="cybersecurity", traitSignal="security_focus"),
            AssessmentOption(id="q4_grow", text="Building production applications with strong technical mentorship", domainSignal="software_engineering", traitSignal="rapid_growth"),
            AssessmentOption(id="q4_imp", text="Solving high-impact predictive challenges with data intelligence", domainSignal="data_science", traitSignal="data_driven"),
            AssessmentOption(id="q4_inn", text="Frontier research and generative intelligence development", domainSignal="ai_ml", traitSignal="frontier_tech"),
            AssessmentOption(id="q4_scale", text="Architecting cloud scalability, zero-downtime automation, and DevOps", domainSignal="cloud_devops", traitSignal="scalability")
        ]
    )
]

@router.get("/questions", response_model=List[AssessmentQuestion])
def get_assessment_questions():
    return ASSESSMENT_QUESTIONS

@router.post("/submit", response_model=StudentProfile)
def submit_assessment(sub: AssessmentSubmission):
    domain_scores: Dict[str, int] = {
        "cybersecurity": 20,
        "software_engineering": 20,
        "data_science": 20,
        "ai_ml": 20,
        "cloud_devops": 20
    }
    work_signals = []
    domain_prefs = []
    problem_style = "Balanced Technical Investigation"
    motivation = "Strong Technical Growth"

    # Evaluate answers
    for q in ASSESSMENT_QUESTIONS:
        selected_opt_id = sub.answers.get(q.id) or next((v for k, v in sub.answers.items() if k.startswith(q.id)), None)
        if selected_opt_id:
            opt = next((o for o in q.options if o.id == selected_opt_id or selected_opt_id.startswith(o.id) or o.id.startswith(selected_opt_id)), None)
            if opt:
                domain_scores[opt.domainSignal] = domain_scores.get(opt.domainSignal, 0) + 25
                work_signals.append(opt.traitSignal)
                if opt.domainSignal not in domain_prefs:
                    domain_prefs.append(opt.domainSignal)
                if q.id == "q2":
                    problem_style = opt.text
                if q.id == "q4":
                    motivation = opt.text

    signals = AssessmentSignals(
        domainPreferences=domain_prefs,
        problemSolvingStyle=problem_style,
        workStyleSignals=work_signals,
        primaryMotivation=motivation,
        careerInterestScores=domain_scores
    )

    profile = get_profile()
    profile.assessmentSignals = signals

    # Transition to PERSONALIZED if profile already has skills or resume!
    if len(profile.skills) > 0 or profile.resumeFile:
        profile.profileState = "PERSONALIZED"
        profile.profileCompleteness = 100
    else:
        profile.profileState = "PROFILE_INCOMPLETE"
        profile.profileCompleteness = 50

    set_profile(profile)
    return profile
