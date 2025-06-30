from pddlpy import DomainProblem

def normalize(atom):
    # e.g. "(on-table milk wood)" → ["on-table","milk","wood"]
    return tuple(str(atom).strip("()").split())

def print_possible_actions(domain_file, problem_file):
    dp = DomainProblem(domain_file, problem_file)

    init_facts = { normalize(f) for f in dp.initialstate() }

    possible = []
    for name in dp.operators():                     # <-- dp
        for op in dp.ground_operator(name):         # <-- dp
            pos = { normalize(p) for p in op.precondition_pos }
            neg = { normalize(n) for n in op.precondition_neg }

                # now pos ≤ init_facts really checks YOUR state
            if pos <= init_facts and not (neg & init_facts):
                possible.append(op)
                print(f"Possible action: {op.operator_name}, params: {op.variable_list}")            
    if not possible:
        print("No possible actions in the initial state.")
    return possible

if __name__ == "__main__":
    print_possible_actions("domain.pddl", "problem.pddl")
