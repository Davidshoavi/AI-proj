import sys
import json
from pddlpy import DomainProblem
import random
import math


class MCTS:
    def __init__(self, similarity, pddl, step_limit, T):
        self.similarity = similarity
        self.pddl = pddl
        self.step_limit = step_limit
        self.T = T

    def play(self, state):
        pass

    def probabilistic_choice(self, delta):
        probability = math.exp(-delta / self.T)
        return random.random() < probability

    def make_simulation(self, state):
        for i in len(range(self.step_limit)):
            chose = False
            while not chose:  # if no action for 30 steps, stop!
                new_node = get_action()  # do get action!
                if self.similarity(new_node) <= self.similarity(state):
                    state = new_node
                    chose = True
                elif self.probabilistic_choice(self.similarity(state) - self.similarity(new_node)):
                    state = new_node
                    chose = True
        return state

                


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
