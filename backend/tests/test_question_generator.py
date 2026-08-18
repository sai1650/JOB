import json

from app.services.question_generator import InterviewQuestionGenerator, QuestionValidationError


class FakeLLM:
    def __init__(self, payload):
        self.payload = payload

    def __call__(self, prompt: str) -> str:
        return json.dumps(self.payload)


def test_question_generator_valid_and_dedupe():
    # llm returns two questions, one duplicate
    chunks = [{"source": "kb1", "page": 1, "text": "Concurrency in python"}]

    def llm(prompt):
        qs = [
            {
                "question": "Explain python concurrency and how to use it in practice.",
                "topic": "concurrency",
                "difficulty": "medium",
                "question_type": "applied",
                "reason": "based on kb",
                "source_context": [{"source": "kb1", "page": 1}],
            },
            {
                "question": "Explain python concurrency and how to use it in practice.",
                "topic": "concurrency",
                "difficulty": "medium",
                "question_type": "applied",
                "reason": "duplicate",
                "source_context": [{"source": "kb1", "page": 1}],
            },
        ]
        return json.dumps(qs)

    gen = InterviewQuestionGenerator(llm=llm)
    out = gen.generate(
        candidate_profile={},
        selected_role={},
        retrieved_context={"chunks": chunks},
        interview_history=[],
        previous_answers=[],
        interview_stage="screening",
        num_questions=5,
    )
    assert "questions" in out
    assert len(out["questions"]) == 1


def test_question_generator_invalid_json():
    def bad_llm(prompt):
        return "not a json"

    gen = InterviewQuestionGenerator(llm=bad_llm)
    try:
        gen.generate({}, {}, {}, [], [], "screening")
        assert False, "should have raised"
    except QuestionValidationError:
        assert True


def test_question_generator_missing_context():
    # LLM cites a source not in retrieved chunks -> rejected
    def llm(prompt):
        qs = [
            {
                "question": "What is X? Explain.",
                "topic": "x",
                "difficulty": "easy",
                "question_type": "conceptual",
                "reason": "test",
                "source_context": [{"source": "unknown", "page": 1}],
            }
        ]
        return json.dumps(qs)

    gen = InterviewQuestionGenerator(llm=llm)
    out = gen.generate({}, {}, {"chunks": []}, [], [], "screening")
    assert out.get("questions") == []
    assert len(out.get("rejected", [])) == 1


def test_question_generator_accepts_valid_questions():
    # retrieved context with one chunk
    retrieved = {
        "chunks": [
            {
                "id": "c1",
                "text": "Python generators",
                "source": "kb/python.pdf",
                "page": 12,
            }
        ]
    }

    valid_questions = [
        {
            "question": (
                "Explain how Python generators work and when you'd use them."
            ),
            "topic": "generators",
            "difficulty": "medium",
            "question_type": "conceptual",
            "reason": "Candidate lists Python as a skill",
            "source_context": [{"source": "kb/python.pdf", "page": 12}],
        }
    ]

    gen = InterviewQuestionGenerator(llm=FakeLLM(valid_questions))
    out = gen.generate(
        candidate_profile={"extracted_skills": ["Python"]},
        selected_role={"title": "Backend"},
        retrieved_context=retrieved,
        interview_history=[],
        previous_answers=[],
        interview_stage="screening",
        num_questions=3,
    )

    assert len(out["questions"]) == 1
    assert out["questions"][0]["topic"] == "generators"


def test_question_generator_rejects_invalid_citation_and_duplicates():
    retrieved = {
        "chunks": [
            {
                "id": "c1",
                "text": "Python generators",
                "source": "kb/python.pdf",
                "page": 12,
            }
        ]
    }

    payload = [
        {
            "question": "Short?",
            "topic": "generators",
            "difficulty": "easy",
            "question_type": "conceptual",
            "reason": "short test",
            "source_context": [{"source": "kb/python.pdf", "page": 12}],
        },
        {
            "question": (
                "Explain how Python generators work and when you'd use them."
            ),
            "topic": "generators",
            "difficulty": "medium",
            "question_type": "conceptual",
            "reason": "candidate skill",
            "source_context": [{"source": "kb/python.pdf", "page": 12}],
        },
        {
            "question": (
                "Explain how Python generators work and when you'd use them."
            ),
            "topic": "generators",
            "difficulty": "medium",
            "question_type": "conceptual",
            "reason": "duplicate",
            "source_context": [{"source": "kb/unknown.pdf", "page": 1}],
        },
    ]

    gen = InterviewQuestionGenerator(llm=FakeLLM(payload))
    out = gen.generate(
        candidate_profile={"extracted_skills": ["Python"]},
        selected_role={"title": "Backend"},
        retrieved_context=retrieved,
        interview_history=[],
        previous_answers=[],
        interview_stage="screening",
        num_questions=5,
    )

    # Only the second question should be accepted; short one rejected,
    # duplicate with invalid citation rejected.
    assert len(out["questions"]) == 1
    assert len(out["rejected"]) >= 2
