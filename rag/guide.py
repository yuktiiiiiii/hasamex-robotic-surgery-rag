from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuideQuestion:
    """One question from the project interview guide."""
    question_id: str
    question: str
    topic: str


INTERVIEW_GUIDE: list[GuideQuestion] = [
    GuideQuestion(
        question_id="Q1",
        topic="Current adoption",
        question="How would you describe current adoption of robotic surgery in your market?",
    ),
    GuideQuestion(
        question_id="Q2",
        topic="Barriers to adoption",
        question="What are the main barriers to adoption?",
    ),
    GuideQuestion(
        question_id="Q3",
        topic="Budget and ROI",
        question="How important are hospital budgets and ROI in purchasing decisions?",
    ),
    GuideQuestion(
        question_id="Q4",
        topic="Training and clinical outcomes",
        question="How important are surgeon training and clinical outcomes?",
    ),
    GuideQuestion(
        question_id="Q5",
        topic="3–5 year adoption trend",
        question="What adoption trend do you expect over the next 3–5 years?",
    ),
    GuideQuestion(
        question_id="Q6",
        topic="Purchase timeline",
        question="What is the typical hospital decision-making timeline for purchasing a new robotic system?",
    ),
]