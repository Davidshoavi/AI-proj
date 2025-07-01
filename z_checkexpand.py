import sys
import json
from pddlpy import DomainProblem
import random
import math
from functions import PDDLState

def test_expand_next_child(domain_file, problem_file):
    # אתחול מצב התחלה
    dp = DomainProblem(domain_file, problem_file)
    state = PDDLState(domain_file=None, problem_file=None, dp_override=dp)

    # וידוא שיש פעולות חוקיות
    print("פעולות חוקיות בשורש:", len(state._applicable_actions))

    # ילדים לפני ההרחבה
    print("מספר ילדים לפני:", len(state.children))

    # הרחבת הילד הבא
    child = state.expand_next_child()
    print("הילד החדש:", child)
    
    # ילדים אחרי ההרחבה
    print("מספר ילדים אחרי:", len(state.children))

    # עובדות במצב החדש מול המקורי
    print("עובדות מצב חדש:", child.facts)
    print("עובדות מצב מקורי עדיין:", state.facts)

if __name__ == "__main__":
    test_expand_next_child("domain.pddl", "problem.pddl")
