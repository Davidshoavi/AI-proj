import json
from pathlib import Path
from functions import get_PDDL, PDDLState, Algoritem

def parse_fact_str(s: str) -> tuple:
    if "(" in s and s.endswith(")"):
        pred, rest = s.split("(", 1)
        args_str = rest[:-1]
        args = args_str.split(",") if args_str else []
        return (pred,) + tuple(args)
    else:
        return (s,)

def run_tests_and_save(vectors_dir="72B", truths_dir="true_states", output_file="test_results.json"):
    # אתחול PDDL
    dp = get_PDDL("domain.pddl", "problem.pddl")
    results = []

    # מיון קבצים מספרית
    vec_paths = sorted(
        Path(vectors_dir).glob("*.json"),
        key=lambda p: int(p.stem.split("_")[-1])
    )

    for vec_path in vec_paths:
        # טען וקטור הסתברויות
        vector = json.loads(vec_path.read_text())

        # הרץ MCTS
        s_init = PDDLState(domain_file=None, problem_file=None, dp_override=dp)
        algo   = Algoritem(str(vec_path), dp, s_init)
        final  = algo.run()
        actual = final.facts

        # 1) סיווג מבוסס וקטור
        predictions = {
            fact_str: True if prob > 0.6 else False
            for fact_str, prob in vector.items()
            if prob > 0.6 or prob < 0.4
        }
        vector_total   = len(predictions)
        vector_correct = sum(
            (parse_fact_str(fact_str) in actual) == pred
            for fact_str, pred in predictions.items()
        )

        # 2) סיווג מול truth_state
        truth_dict   = json.loads((Path(truths_dir)/vec_path.name).read_text())
        truth_total  = len(truth_dict)
        truth_correct = sum(
            (parse_fact_str(fact_str) in actual) == exp
            for fact_str, exp in truth_dict.items()
        )

        results.append({
            "filename": vec_path.name,
            "vector_correct": vector_correct,
            "vector_total": vector_total,
            "truth_correct": truth_correct,
            "truth_total": truth_total
        })

    # חישוב תקציר
    n = len(results)
    avg_vector_acc = sum(r["vector_correct"]/r["vector_total"]
                         for r in results if r["vector_total"]>0) / n
    avg_truth_acc  = sum(r["truth_correct"]/r["truth_total"]
                         for r in results) / n
    both_100_count = sum(
        1 for r in results
        if r["vector_correct"]==r["vector_total"] and r["truth_correct"]==r["truth_total"]
    )

    summary = {
        "average_vector_accuracy": avg_vector_acc,
        "average_truth_accuracy": avg_truth_acc,
        "both_100_count": both_100_count
    }

    # שמירה ל־JSON
    output = {"results": results, "summary": summary}
    Path(output_file).write_text(json.dumps(output, indent=2))

    print(f"Saved test results to {output_file}")

if __name__ == "__main__":
    run_tests_and_save()
