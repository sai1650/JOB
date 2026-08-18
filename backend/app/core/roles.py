from typing import Dict, List


ROLES: Dict[str, Dict] = {
    "ai_ml_engineer": {
        "name": "AI/ML Engineer",
        "description": (
            "Build and productionize ML systems, models and pipelines."
        ),
        "core_topics": [
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "Model Evaluation",
            "Feature Engineering",
            "MLOps",
        ],
        "important_skills": [
            "python",
            "pytorch",
            "tensorflow",
            "mlops",
            "docker",
        ],
        "difficulty_distribution": {"easy": 0.2, "medium": 0.6, "hard": 0.2},
        "knowledge_base": "ai_ml",
        "interview_focus": ["modeling", "evaluation", "deployment"],
    },
    "backend_engineer": {
        "name": "Backend Engineer",
        "description": (
            "Design and implement scalable backend systems and APIs."
        ),
        "core_topics": [
            "Python",
            "APIs",
            "FastAPI",
            "Databases",
            "SQL",
            "System Design",
            "Distributed Systems",
        ],
        "important_skills": [
            "python",
            "fastapi",
            "sql",
            "docker",
            "kubernetes",
        ],
        "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
        "knowledge_base": "backend",
        "interview_focus": ["apis", "data modeling", "scalability"],
    },
    "data_scientist": {
        "name": "Data Scientist",
        "description": "Analyze data, build models, and communicate insights.",
        "core_topics": [
            "Statistics",
            "ML",
            "Data Visualization",
            "Experimentation",
        ],
        "important_skills": ["python", "pandas", "sql", "statistics"],
        "difficulty_distribution": {"easy": 0.25, "medium": 0.6, "hard": 0.15},
        "knowledge_base": "data_science",
        "interview_focus": ["analysis", "modeling", "communication"],
    },
    "data_analyst": {
        "name": "Data Analyst",
        "description": (
            "Prepare and analyze data to support business decisions."
        ),
        "core_topics": ["SQL", "Data Cleaning", "Dashboards", "Statistics"],
        "important_skills": ["sql", "excel", "tableau", "python"],
        "difficulty_distribution": {"easy": 0.4, "medium": 0.5, "hard": 0.1},
        "knowledge_base": "data_analytics",
        "interview_focus": ["sql", "analysis", "visualization"],
    },
}


def list_roles() -> List[Dict]:
    return [{"id": key, **val} for key, val in ROLES.items()]


def get_role(role_id: str) -> Dict:
    return ROLES.get(role_id)
