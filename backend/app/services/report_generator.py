from typing import Dict, List, Any
from datetime import datetime


def _avg(lst: List[float]) -> float:
    if not lst:
        return 0.0
    return sum(lst) / len(lst)


def generate_report(session: Any, candidate: Any, questions: List[Any], answers: List[Any]) -> Dict[str, Any]:
    qmap = {q.id: q for q in questions}

    topic_scores = {}
    topic_counts = {}
    diff_scores = {}
    diff_counts = {}
    progression = []

    for idx, a in enumerate(sorted(answers, key=lambda x: x.created_at)):
        q = qmap.get(a.question_id)
        score = float(a.evaluation_score or 0.0)
        topic = (q.topic or 'general') if q else 'general'
        diff = (q.difficulty or 'unknown') if q else 'unknown'

        topic_scores.setdefault(topic, 0.0)
        topic_counts.setdefault(topic, 0)
        topic_scores[topic] += score
        topic_counts[topic] += 1

        diff_scores.setdefault(diff, 0.0)
        diff_counts.setdefault(diff, 0)
        diff_scores[diff] += score
        diff_counts[diff] += 1

        if hasattr(a.created_at, 'isoformat'):
            ts = a.created_at.isoformat()
        else:
            ts = str(a.created_at)
        progression.append({
            'step': idx + 1,
            'question_id': a.question_id,
            'topic': topic,
            'difficulty': diff,
            'score': score,
            'feedback': a.evaluation_feedback,
            'timestamp': ts,
        })

    perf_by_topic = {
        t: (topic_scores[t] / max(1, topic_counts[t]))
        for t in topic_scores
    }
    perf_by_difficulty = {
        d: (diff_scores[d] / max(1, diff_counts[d]))
        for d in diff_scores
    }

    overall = _avg([float(a.evaluation_score or 0.0) for a in answers])

    strengths = [t for t, v in perf_by_topic.items() if v >= 0.75]
    weaknesses = [t for t, v in perf_by_topic.items() if v <= 0.5]

    all_topics = set((q.topic or 'general') for q in questions)
    answered_topics = set(topic_counts.keys())
    unanswered_topics = list(all_topics - answered_topics)

    extra_weak = [t for t in weaknesses if t not in unanswered_topics]
    knowledge_gaps = list(unanswered_topics) + extra_weak

    recommended = []
    for t in weaknesses:
        recommended.append(f"Review fundamentals and practice problems in {t}")
    for t in unanswered_topics:
        recommended.append(
            f"Study foundational concepts in {t} and attempt applied exercises"
        )

    exec_lines = []
    exec_lines.append(
        "Interview completed for candidate "
        + f"{session.candidate_id} for role {session.selected_role}."
    )
    overall_pct = f"{(overall*100):.0f}%"
    overall_rest = f" across {len(answers)} answered questions."
    exec_lines.append("Overall score: " + overall_pct + overall_rest)
    if strengths:
        exec_lines.append(f"Strengths observed in: {', '.join(strengths)}.")
    if weaknesses:
        exec_lines.append(
            "Areas needing improvement: " + f"{', '.join(weaknesses)}."
        )

    exec_summary = ' '.join(exec_lines)

    if overall >= 0.8:
        overall_assessment = "Candidate shows strong command across topics."
    elif overall >= 0.6:
        overall_assessment = (
            "Candidate demonstrates solid fundamentals but gaps remain."
        )
    else:
        overall_assessment = (
            "Candidate requires further evaluation and development in "
            "several areas."
        )

    if overall >= 0.8:
        hiring = 'Strong Fit'
    elif overall >= 0.6:
        hiring = 'Potential Fit'
    else:
        hiring = 'Needs Further Evaluation'

    report = {
        'generated_at': datetime.utcnow().isoformat(),
        'executive_summary': exec_summary,
        'technical_strengths': strengths,
        'technical_weaknesses': weaknesses,
        'knowledge_gaps': knowledge_gaps,
        'performance_by_topic': perf_by_topic,
        'performance_by_difficulty': perf_by_difficulty,
        'interview_progression': progression,
        'recommended_learning_areas': recommended,
        'overall_assessment': overall_assessment,
        'overall_score': overall,
        'hiring_recommendation': hiring,
    }

    return report
