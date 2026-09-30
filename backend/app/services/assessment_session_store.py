from typing import Dict, Any, Optional, List, Set
import time
from ..schemas.assessment import (
    AssessmentSessionState,
    AdaptiveQuestionView,
    AdaptiveOptionView,
    PracticalScenarioView,
    CareerIntelligenceProfile,
    DomainInterestItem,
    ConfidenceLevel,
    InterestRating
)
from ..intelligence.adaptive_assessment_engine import (
    adaptive_assessment_engine,
    QUESTION_BANK,
    PRACTICAL_CHALLENGES,
    DOMAIN_MAP,
    CANONICAL_DOMAINS
)
from ..api.routes.profile_store import get_profile, set_profile

class AssessmentSession:
    def __init__(self, user_id: str):
        self.sessionId: str = f"sess_{abs(hash(user_id + str(time.time()))) % 1000000}"
        self.userId: str = user_id
        self.currentPhase: str = "MIXED_DISCOVERY"
        self.discoveryQueue: List[Dict[str, Any]] = adaptive_assessment_engine.get_discovery_questions()
        self.discoveryIndex: int = 0
        self.currentAdaptiveQuestion: Optional[Dict[str, Any]] = None
        self.currentPracticalScenario: Optional[Dict[str, Any]] = None
        self.answers: Dict[str, str] = {}  # question_id -> option_id
        self.confidences: Dict[str, ConfidenceLevel] = {}  # question_id -> confidence
        self.interestRatings: Dict[str, InterestRating] = {d["id"]: "interested" for d in CANONICAL_DOMAINS}
        self.scenarioPreference: Optional[str] = None
        self.practicalScores: Dict[str, int] = {}
        self.practicalFeedback: Dict[str, str] = {}
        self.preliminarySignals: Dict[str, int] = {}
        self.isComplete: bool = False
        self.profile: Optional[CareerIntelligenceProfile] = None

    def total_answered_count(self) -> int:
        return len(self.answers)

    def to_question_view(self, q: Dict[str, Any], number: int, is_adaptive: bool = False, note: Optional[str] = None) -> AdaptiveQuestionView:
        options = [
            AdaptiveOptionView(id=opt["id"], text=opt["text"])
            for opt in q["options"]
        ]
        d_label = DOMAIN_MAP.get(q["domain"], {}).get("label", q["domain"].title())
        return AdaptiveQuestionView(
            id=q["id"],
            number=number,
            totalEstimatedQuestions=16,
            domain=q["domain"],
            domainLabel=d_label,
            skill=q["skill"],
            difficulty=q["difficulty"].title(),
            questionType=q["questionType"].replace("_", " ").title(),
            question=q["question"],
            scenario=q.get("scenario"),
            options=options,
            phase=self.currentPhase,
            isAdaptiveFollowUp=is_adaptive,
            contextNote=note
        )

# In-memory session tracking
_active_sessions: Dict[str, AssessmentSession] = {}

class AssessmentSessionStore:
    @classmethod
    def get_or_create_session(cls, user_id: str, force_new: bool = False) -> AssessmentSession:
        if force_new or user_id not in _active_sessions:
            sess = AssessmentSession(user_id)
            _active_sessions[user_id] = sess
            return sess
        return _active_sessions[user_id]

    @classmethod
    def reset_session(cls, user_id: str) -> AssessmentSession:
        return cls.get_or_create_session(user_id, force_new=True)

    @classmethod
    def get_session(cls, user_id: str) -> Optional[AssessmentSession]:
        return _active_sessions.get(user_id)

    @classmethod
    def get_state(cls, user_id: str) -> AssessmentSessionState:
        sess = cls.get_or_create_session(user_id)

        current_q_view = None
        current_prac_view = None

        if sess.currentPhase == "MIXED_DISCOVERY":
            if sess.discoveryIndex < len(sess.discoveryQueue):
                raw_q = sess.discoveryQueue[sess.discoveryIndex]
                current_q_view = sess.to_question_view(raw_q, sess.total_answered_count() + 1, is_adaptive=False)
        elif sess.currentPhase == "ADAPTIVE_EXPLORATION":
            if sess.currentAdaptiveQuestion:
                note = f"Calibrating problem-solving depth in {DOMAIN_MAP.get(sess.currentAdaptiveQuestion['domain'], {}).get('label', '')} based on previous responses."
                current_q_view = sess.to_question_view(
                    sess.currentAdaptiveQuestion,
                    sess.total_answered_count() + 1,
                    is_adaptive=True,
                    note=note
                )
        elif sess.currentPhase == "PRACTICAL_CHALLENGE":
            if sess.currentPracticalScenario:
                p = sess.currentPracticalScenario
                current_prac_view = PracticalScenarioView(
                    id=p["id"],
                    domain=p["domain"],
                    domainLabel=p["domainLabel"],
                    title=p["title"],
                    scenarioText=p["scenarioText"],
                    contextSnippet=p.get("contextSnippet"),
                    options=[AdaptiveOptionView(id=o["id"], text=o["text"]) for o in p["options"]]
                )

        return AssessmentSessionState(
            sessionId=sess.sessionId,
            userId=sess.userId,
            currentPhase=sess.currentPhase,
            questionNumber=sess.total_answered_count() + 1,
            totalEstimatedQuestions=16,
            questionsAnsweredCount=sess.total_answered_count(),
            currentQuestion=current_q_view,
            currentPracticalScenario=current_prac_view,
            isComplete=sess.isComplete,
            preliminarySignals=sess.preliminarySignals if sess.preliminarySignals else None,
            profile=sess.profile
        )

    @classmethod
    def answer_question(
        cls,
        user_id: str,
        question_id: str,
        selected_option_id: str,
        confidence: ConfidenceLevel = "confident"
    ) -> AssessmentSessionState:
        sess = cls.get_or_create_session(user_id)

        sess.answers[question_id] = selected_option_id
        sess.confidences[question_id] = confidence

        # Phase 1: Mixed Discovery
        if sess.currentPhase == "MIXED_DISCOVERY":
            sess.discoveryIndex += 1
            if sess.discoveryIndex >= len(sess.discoveryQueue):
                # Completed initial 10 mixed questions -> Calculate preliminary signals
                demonstrated, evidence, skills, conf_sigs, strength = adaptive_assessment_engine.calculate_domain_knowledge_signals(
                    sess.answers, sess.confidences
                )
                sess.preliminarySignals = demonstrated
                sess.currentPhase = "ADAPTIVE_EXPLORATION"

                # Pick first adaptive question
                next_q = adaptive_assessment_engine.select_next_adaptive_question(
                    set(sess.answers.keys()),
                    demonstrated,
                    evidence,
                    sess.total_answered_count()
                )
                sess.currentAdaptiveQuestion = next_q

        # Phase 2: Adaptive Exploration
        elif sess.currentPhase == "ADAPTIVE_EXPLORATION":
            demonstrated, evidence, skills, conf_sigs, strength = adaptive_assessment_engine.calculate_domain_knowledge_signals(
                sess.answers, sess.confidences
            )
            sess.preliminarySignals = demonstrated

            total_answered = sess.total_answered_count()

            # Check stopping conditions:
            # 1. Answered >= 15 questions and top domains have >= 2 evidence count each, OR
            # 2. Answered >= MAX_QUESTIONS (20 questions)
            should_stop = False
            if total_answered >= adaptive_assessment_engine.MIN_QUESTIONS:
                strong_domains = [d for d, s in demonstrated.items() if s >= 65]
                if not strong_domains or all(evidence.get(d, 0) >= 2 for d in strong_domains):
                    should_stop = True

            if total_answered >= adaptive_assessment_engine.MAX_QUESTIONS:
                should_stop = True

            if should_stop:
                sess.currentPhase = "INTEREST_DISCOVERY"
                sess.currentAdaptiveQuestion = None
            else:
                next_q = adaptive_assessment_engine.select_next_adaptive_question(
                    set(sess.answers.keys()),
                    demonstrated,
                    evidence,
                    total_answered
                )
                if next_q:
                    sess.currentAdaptiveQuestion = next_q
                else:
                    sess.currentPhase = "INTEREST_DISCOVERY"
                    sess.currentAdaptiveQuestion = None

        return cls.get_state(user_id)

    @classmethod
    def submit_interests(
        cls,
        user_id: str,
        domain_interests: List[DomainInterestItem],
        scenario_preference: Optional[str] = None
    ) -> AssessmentSessionState:
        sess = cls.get_or_create_session(user_id)

        for item in domain_interests:
            sess.interestRatings[item.domain] = item.interestLevel

        if scenario_preference:
            sess.scenarioPreference = scenario_preference

        # Choose best practical challenge corresponding to student's strongest domain
        demonstrated = sess.preliminarySignals
        if not demonstrated:
            demonstrated, _, _, _, _ = adaptive_assessment_engine.calculate_domain_knowledge_signals(
                sess.answers, sess.confidences
            )

        # Sort domains by demonstrated knowledge descending
        sorted_domains = sorted(demonstrated.items(), key=lambda x: x[1], reverse=True)
        top_domain = sorted_domains[0][0] if sorted_domains else "cybersecurity"

        # If user expressed very high interest in another domain with score >= 50, consider that
        for item in domain_interests:
            if item.interestLevel == "very_interested" and demonstrated.get(item.domain, 0) >= 50:
                top_domain = item.domain
                break

        sess.currentPracticalScenario = PRACTICAL_CHALLENGES.get(top_domain, PRACTICAL_CHALLENGES["cybersecurity"])
        sess.currentPhase = "PRACTICAL_CHALLENGE"

        return cls.get_state(user_id)

    @classmethod
    def submit_practical(
        cls,
        user_id: str,
        scenario_id: str,
        selected_option_id: str,
        reasoning: Optional[str] = ""
    ) -> CareerIntelligenceProfile:
        sess = cls.get_or_create_session(user_id)

        score, feedback = adaptive_assessment_engine.evaluate_practical_challenge(
            scenario_id, selected_option_id, reasoning
        )

        domain_key = "cybersecurity"
        if sess.currentPracticalScenario:
            domain_key = sess.currentPracticalScenario["domain"]

        sess.practicalScores[domain_key] = score
        sess.practicalFeedback[domain_key] = feedback

        # Finalize and generate CareerIntelligenceProfile
        demonstrated, evidence, skills, conf_sigs, strength = adaptive_assessment_engine.calculate_domain_knowledge_signals(
            sess.answers, sess.confidences
        )

        intel_profile = adaptive_assessment_engine.build_career_intelligence_profile(
            user_id=user_id,
            demonstrated_scores=demonstrated,
            domain_evidence_counts=evidence,
            skills_demonstrated=skills,
            confidence_signals=conf_sigs,
            evidence_strength=strength,
            interest_ratings=sess.interestRatings,
            scenario_preference=sess.scenarioPreference,
            practical_scores=sess.practicalScores,
            total_questions_answered=sess.total_answered_count()
        )

        sess.profile = intel_profile
        sess.isComplete = True
        sess.currentPhase = "COMPLETED"

        # Apply to canonical student profile
        student_profile = get_profile()
        adaptive_assessment_engine.apply_assessment_to_student_profile(student_profile, intel_profile)
        set_profile(student_profile)

        return intel_profile

assessment_session_store = AssessmentSessionStore()
