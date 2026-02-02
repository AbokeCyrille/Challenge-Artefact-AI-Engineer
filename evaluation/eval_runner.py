from evaluation.datasets import EVAL_SET
from agents.router import route
from evaluation.metrics import numeric_match

def run_eval():
    results = []

    for test in EVAL_SET:
        resp = route(test["question"])
        success = False
        reason = None

        if test["type"] == "fact":
            answer = resp.get("answer", "").lower()
            success = test["expected"].lower() in answer
            if not success:
                reason = "expected string not found in answer"

        elif test["type"] == "aggregation":
            table = resp.get("table")

            if table is None or table.empty:
                success = False
                reason = "no table returned"
            else:
                value = table.iloc[0, 0]
                success = numeric_match(
                    value,
                    test["expected"],
                    test.get("tolerance", 0)
                )
                if not success:
                    reason = f"value mismatch: got {value}"

        results.append({
            "question": test["question"],
            "type": test["type"],
            "success": success,
            "reason": reason,
            "response": resp, 
            "response_type": resp.get("type"),
        })

    return results

def summarize(results):
    total = len(results)
    passed = sum(r["success"] for r in results)

    by_type = {}
    for r in results:
        t = r.get("response_type", "unknown")
        by_type.setdefault(t, {"total": 0, "passed": 0})
        by_type[t]["total"] += 1
        if r["success"]:
            by_type[t]["passed"] += 1

    return {
        "accuracy": passed / total if total else 0,
        "total": total,
        "passed": passed,
        "by_type": by_type
    }



