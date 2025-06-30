import sys
import json
from pddlpy import DomainProblem
import random
import math


class MCTS:
    def __init__(self, similarity, step_limit, T, starting_state, rounds):
        self.similarity = similarity

        self.step_limit = step_limit
        self.T = T
        self.starting_state = starting_state
        self.rounds = rounds

    def play(self):
        min_node = self.starting_state

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
            if self.similarity(result) < self.similarity(min_node):

                min_node = result

            # 4. Backpropagation
            self.backpropagation(result, node)
        
        return min_node

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


def get_PDDL(domain_file, problem_file):
    return DomainProblem(domain_file, problem_file)


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
            self.facts = { self.normalize(atom) for atom in self.dp.initialstate() }

        self.children = []
        self.parent = parent
        self.visits = 0
        self.similarity_score = similarity_score

        self._applicable_actions = self.applicable_actions()
        self.num_applicable_actions = len(self._applicable_actions)
        self.fully_expanded = False
        if len(self._applicable_actions) == 0:
            self.fully_expanded = True

    def normalize(self,atom):
        # e.g. "(on-table milk wood)" → ["on-table","milk","wood"]
        if hasattr(atom, 'predicate') and hasattr(atom, 'args'):
            return (atom.predicate, ) + tuple(atom.args)
        # גיבוי: מחרוזת בלי גרשיים
        text = str(atom).strip("()").replace("'", "")
        return tuple(text.split())

    def applicable_actions(self):
        init_facts = set(self.facts)

        possible = []
        for name in self.dp.operators():                     # <-- self.dp
            for op in self.dp.ground_operator(name):         # <-- self.dp
                pos = { self.normalize(p) for p in op.precondition_pos }
                neg = { self.normalize(n) for n in op.precondition_neg }

                # now pos ≤ init_facts really checks YOUR state
                if pos <= init_facts and not (neg & init_facts):
                    possible.append(op)
        return possible
    
    def size(self):
        return len(self.facts)

    def apply_action(self, action, similarity_score=0.0):
        new_facts = set(self.facts)
        eff_pos = action.effect_pos
        eff_neg = action.effect_neg

        for atom in action.effect_neg:
            new_facts.discard(self.normalize(atom))

        for atom in action.effect_pos:
            new_facts.add(self.normalize(atom))

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
    
    def __str__(self):
        lines = []
        lines.append("Predicates in state:")
        for pred in self.facts:
            lines.append(f"  {pred}")

        # חשב מרחק באמצעות פונקציית distance_func
        try:
            if not hasattr(self, "distance_func") or self.distance_func is None:
                raise RuntimeError("No distance function provided")
            distance = self.distance_func(self)
            lines.append(f"Distance from probability vector: {distance}")
        except Exception:
            lines.append("Distance: unavailable (no distance function)")

        return "\n".join(lines)


class Algoritem:
    def __init__(self, probabilities, pddl, s_init):
        self.pddl = pddl
        self.s_init = s_init
        self.similarity = self.get_distance_func()
        with open(probabilities, "r") as f:
            self.vector = json.load(f)

    def get_distance_func(self):
        def similarity(state):
            distance = 0.0
            for pred_str, prob in self.vector.items():
                truth_value = 1.0 if pred_str in state.facts else 0.0
                distance += abs(truth_value - prob)
            return distance
        return similarity
    
    def run(self):
        t = 1
        s = self.s_init
        for i in range(10):
            #print(f"\n=== Iteration {i+1} ===")
            #print(f"Facts BEFORE: {list(s.facts)}")
            mcts = MCTS(self.similarity, 10, t, s, 10)
            s_new = mcts.play()
            #print(f"Facts AFTER: {list(s_new.facts)}")
            changed = s_new.facts != s.facts
            #print("State changed?" , changed)
            s = s_new
            t *= 0.95
        return s
    
    #  def run(self):
    #     t = 1
    #     s = self.s_init
    #     for i in range(10):
    #         if s is None:
    #             print("None")
    #         else:
    #             print("no None")
    #         mcts = MCTS(self.similarity, 100, t, s, 100)
    #         s = mcts.play()
    #         t *= 0.95
    #     return s


if __name__ == "__main__":
    dp = get_PDDL("domain.pddl", "problem.pddl")
    s_init = PDDLState(domain_file=None, problem_file=None, dp_override=dp)
    algo = Algoritem("vector.json", dp, s_init)
    print (algo.run())
