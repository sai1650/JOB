from app.services.evaluator import Evaluator, EvaluationResult


def make_retrieved(texts):
    return {"chunks": [{"text": t} for t in texts]}


def test_excellent_answer():
    retrieved = make_retrieved(["Python generators and list comprehensions are memory efficient."])
    answer = "Generators are memory efficient because they yield items lazily; for example using (x for x in seq) instead of building a list. This reduces memory usage."
    ev = Evaluator()
    res = ev.evaluate(answer, "Explain generators vs lists", retrieved)
    assert isinstance(res, EvaluationResult)
    assert res.score >= 6
    assert res.verdict in ("correct", "partially_correct")


def test_partial_answer():
    retrieved = make_retrieved(["Use list comprehensions for compact code." ])
    answer = "You can use list comprehensions to make code compact."
    ev = Evaluator()
    res = ev.evaluate(answer, "When to use list comprehensions", retrieved)
    assert res.score >= 3
    assert res.score < 8
    assert res.verdict == "partially_correct"


def test_incorrect_answer():
    retrieved = make_retrieved(["Databases use transactions to ensure consistency."])
    answer = "You should always store all data in flat files for speed."
    ev = Evaluator()
    res = ev.evaluate(answer, "Why use transactions?", retrieved)
    assert res.score <= 4
    assert res.verdict == "incorrect"


def test_empty_answer():
    retrieved = make_retrieved(["OAuth2 uses access tokens and refresh tokens."])
    answer = ""
    ev = Evaluator()
    res = ev.evaluate(answer, "Describe OAuth2 tokens", retrieved)
    assert res.score == 0
    assert "No answer" in res.feedback or "No answer" in res.feedback


def test_malformed_llm_response_falls_back():
    # LLM returns non-json -> evaluator should fall back to rule-based
    def bad_llm(prompt: str):
        return "THIS IS NOT JSON"

    retrieved = make_retrieved(["Python decorators wrap functions and can modify behavior."])
    answer = "Decorators can wrap functions to add behavior."
    ev = Evaluator(llm=bad_llm)
    res = ev.evaluate(answer, "What are decorators?", retrieved)
    assert isinstance(res, EvaluationResult)
    assert "falling back" in res.feedback or "LLM evaluation failed" in res.feedback
