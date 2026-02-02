from agents.router import route

def test_rhdp_seats():
    resp = route("How many seats did RHDP win?")
    assert "RHDP" in resp["answer"]

def test_ambiguous_query():
    resp = route("Who won in Abidjan?")
    assert resp["type"] == "clarification"
