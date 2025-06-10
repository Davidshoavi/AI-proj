import sys
import json
from pddlpy import DomainProblem
import random
import math


class MCTS:
    def __init__(self, similarity, pddl_domain, pddl_problem, step_limit, T, starting_state, rounds):
        self.similarity = similarity
        self.pddl_domain = pddl_domain
        self.pddl_problem  = pddl_problem
        self.step_limit = step_limit
        self.T = T
        self.starting_state = starting_state
        self.rounds = rounds

    def play(self):
        for _ in range(self.rounds):
            # 1. Selection
            node = self.starting_state
            while node.fully_expanded and node.children:
                node = max(node.children, key=lambda child: child.ucb())

            # 2. Expansion
            if not node.fully_expanded:
                node = node.expand_next_child()
            
            else:
                pass  # think

            # 3. Simulation
            result = self.make_simulation(node)

            # 4. Backpropagation
            self.backpropagation(result, node)

    def probabilistic_choice(self, delta):
        probability = math.exp(-delta / self.T)
        return random.random() < probability

    def get_next_state(self, state):
        actions = state.applicable_actions()
        if not actions:
            return state  # אין פעולות – מחזיר את עצמו
        return state.apply_action(random.choice(actions))

    def make_simulation(self, state):
        min_state = state
        for _ in range(self.step_limit):
            chose = False
            tries = 0
            while not chose and tries < 30:
                new_node = self.get_next_state(state)
                tries += 1
                new_sim = self.similarity(new_node)
                old_sim = self.similarity(state)
                if new_sim <= old_sim or self.probabilistic_choice(old_sim - new_sim):
                    state = new_node
                    chose = True
                    if new_sim < self.similarity(min_state):
                        min_state = new_node
            if not chose:
                break  # נתקענו – מפסיקים את הסימולציה
        return min_state
    
    def backpropagation(self, result, node):
        node.update_similarity(self.similarity(result))
        node.increment_visits()
        while node is not self.starting_state:
            node = node.parent
            node.update_similarity(self.similarity(result))
            node.increment_visits()

                


def get_probabilities():  # improve
    probabilities_file = sys.args[3]
    with open(probabilities_file) as f:
        probabilities = json.load(f)
    # sys.args[3]
    # return probabilities
    return probabilities


def get_PDDL():
    # sys.argv[1], sys.argv[2]
    # return DomainProblem(domain_file, problem_file)
    pass






class PDDLState:
    C = 1.0

    def __init__(
        self,
        domain_file,
        problem_file,
        facts_override=None,
        dp_override=None,
        parent=None,
        similarity_score=0.0
    ):
        if dp_override:
            self.dp = dp_override
        else:
            self.dp = DomainProblem(domain_file, problem_file)

        if facts_override is not None:
            self.facts = set(facts_override)
        else:
            self.facts = set(self.dp.initialstate())

        self.children = []
        self.parent = parent
        self.visits = 0
        self.similarity_score = similarity_score

        self._applicable_actions = self.applicable_actions()
        self.num_applicable_actions = len(self._applicable_actions)
        self.fully_expanded = False

    def applicable_actions(self):
        applicable = []
        for action_name in self.dp.operators():
            for grounded_op in self.dp.ground_operator(action_name):
                pre_pos, pre_neg = grounded_op.precond
                if all(p in self.facts for p in pre_pos) and all(n not in self.facts for n in pre_neg):
                    applicable.append(grounded_op)
        return applicable

    def size(self):
        return len(self.facts)

    def apply_action(self, action, similarity_score=0.0):
        new_facts = set(self.facts)
        eff_pos, eff_neg = action.effect

        for fact in eff_neg:
            new_facts.discard(fact)
        for fact in eff_pos:
            new_facts.add(fact)

        new_state = PDDLState(
            domain_file=None,
            problem_file=None,
            facts_override=new_facts,
            dp_override=self.dp,
            parent=self,
            similarity_score=similarity_score
        )
        self.children.append(new_state)
        self._update_fully_expanded()
        return new_state

    def expand_next_child(self):
        if self.fully_expanded:
            return None
        next_action = self._applicable_actions[len(self.children)]
        return self.apply_action(next_action)

    def increment_visits(self):
        self.visits += 1

    def update_similarity(self, new_score):
        self.similarity_score = (
            self.similarity_score * self.visits + new_score
        ) / (self.visits + 1)

    def ucb(self):
        if self.visits == 0 or self.parent is None or self.parent.visits == 0:
            return float('inf')
        import math
        return (
            PDDLState.C * math.sqrt(math.log(self.parent.visits) / self.visits)
            + (1 - self.similarity_score)
        )

    def __eq__(self, other):
        if not isinstance(other, PDDLState):
            return False
        return self.facts == other.facts

    def _update_fully_expanded(self):
        self.fully_expanded = (len(self.children) == self.num_applicable_actions)


class Algoritem():
    def __init__(self, probabilities, pddl, s_init):
        pass

    def get_distance_func(self):
        def similarity(state):
            pass
        return similarity
    
    def run():
        pass

    def changeT():
        pass

    def do_again():
        pass


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python your_program.py <domain.pddl> <problem.pddl>")
        sys.exit(1)

    probabilities = get_probabilities()
    dp = get_PDDL()
