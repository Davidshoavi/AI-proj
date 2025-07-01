import json
from pathlib import Path
from functions import get_PDDL, PDDLState, Algoritem

def parse_fact_str(s: str) -> tuple:
    """
    Parse a truth-JSON key into a tuple:
      - "pred(arg1,arg2,…)" → ("pred","arg1","arg2",…)
      - "pred"               → ("pred",)
    """
    if "(" in s and s.endswith(")"):
        pred, rest = s.split("(", 1)
        args_str = rest[:-1]              # drop trailing ')'
        args = args_str.split(",") if args_str else []
        return (pred,) + tuple(args)
    else:
        return (s,)

def batch_test(vectors_dir: str = "72B", truths_dir: str = "true_states"):
    dp     = get_PDDL("domain.pddl", "problem.pddl")
    correct = total = 0

    # בחר עד 300 קבצים, ממוינים לפי המספר בסוף השם
    vec_paths = sorted(
        Path(vectors_dir).glob("*.json"),
        key=lambda p: int(p.stem.split("_")[-1])
    )[:6]

    for vec_path in vec_paths:
        total += 1
        # כל איטרציה מתחילה ממצב תחלתי חדש
        s_init = PDDLState(domain_file=None,
                           problem_file=None,
                           dp_override=dp)

        print(f"\n=== Testing vector: {vec_path.name}")
        truth_path = Path(truths_dir) / vec_path.name
        print(f"    truth file: {truth_path.name}")

        # הרץ MCTS
        algo  = Algoritem(str(vec_path), dp, s_init)
        final = algo.run()
        actual = final.facts

        # טען ופרש את ה-truth dict (רק ערכים True)
        truth_dict = json.loads(truth_path.read_text())
        expected   = {
            parse_fact_str(k)
            for k, v in truth_dict.items()
            if v is True
        }

        # חישוב מדדים
        present = actual & expected
        missing = expected - actual
        extra   = actual - expected

        # הדפס תוצאות
        print(f"{len(present)} ")
        print(f"    {len(present)}/{len(expected)} expected facts are present")
        print(extra)
        print(f"    {len(extra)} extra facts in actual state")

        # PASS אם לא חסר כלום
        if not missing:
            print("✔ PASS")
            correct += 1
        else:
            print("❌ FAIL")
            print(f"    Missing facts: {missing}")

    print(f"\nSummary: {correct}/{total} passed.")

if __name__ == "__main__":
    batch_test("72B", "true_states")
