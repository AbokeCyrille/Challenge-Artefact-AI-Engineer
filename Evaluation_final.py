from evaluation.eval_runner import run_eval, summarize

if __name__ == "__main__":
    results = run_eval()
    summary = summarize(results)

    print("=== EVALUATION SUMMARY ===")
    print(summary)

    print("\n=== FAILURES ===")
    for r in results:
        if not r["success"]:
            print(f"- {r['question']}")
            print("  Response:", r["response"].get("answer", "<no answer>"))
            print("  Reason:", r.get("reason"))
