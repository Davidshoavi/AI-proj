import sys
import json
from pddlpy import DomainProblem
import random
import math
from functions import PDDLState

def test_apply_action(domain_file, problem_file):
    # 1. בונים את ה‐DomainProblem ואת המצב ההתחלתי
    dp = DomainProblem(domain_file, problem_file)
    state = PDDLState(domain_file=None, problem_file=None, dp_override=dp)

    # 2. שולפים פעולה חוקית ראשונה
    actions = state.applicable_actions()
    if not actions:
        print("אין פעולות חוקיות להפעיל במצב ההתחלתי.")
        return
    action = actions[0]
    print("choosen action:", action.operator_name, action.variable_list)

    # 3. עובדות לפני ההפעלה
    before = set(state.facts)
    print("before", before)

    # 4. הפעלת הפעולה
    new_state = state.apply_action(action)

    # 5. עובדות אחרי ההפעלה
    after = set(new_state.facts)
    print("after", after)

    # 6. מה התווסף ומה הוסר
    print("added:", after - before)
    print("delete:", before - after)

# קריאה לבדיקה
if __name__ == "__main__":
    test_apply_action("domainGPT.pddl", "problemGPT.pddl")
