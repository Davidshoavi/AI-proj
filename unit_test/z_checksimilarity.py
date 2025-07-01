import unittest

def get_distance_func(vector):
    def similarity(state):
        fact_strs = {' '.join(f) for f in state.facts}
        distance = 0.0
        for pred_str, prob in vector.items():
            truth_value = 1.0 if pred_str in fact_strs else 0.0
            distance += abs(truth_value - prob)
        return distance
    return similarity

class DummyState:
    def __init__(self, facts):
        # facts = set of tuples representing predicates in state
        self.facts = facts

class TestSimilarity(unittest.TestCase):
    def setUp(self):
        # דוגמה ל־vector.json
        self.vector = {
            "on-table milk-carton wood-table": 0.2,
            "robot-gripper-empty": 1.0,
            "robot-gripping milk-carton": 0.0
        }
        self.similarity = get_distance_func(self.vector)

    def test_all_facts_present(self):
        state = DummyState({
            ("on-table", "milk-carton", "wood-table"),
            ("robot-gripper-empty",)
        })
        expected = abs(1.0 - 0.2) + abs(1.0 - 1.0) + abs(0.0 - 0.0)
        self.assertAlmostEqual(self.similarity(state), expected)

    def test_some_facts_missing(self):
        state = DummyState({
            ("on-table", "milk-carton", "wood-table"),
        })
        expected = abs(1.0 - 0.2) + abs(0.0 - 1.0) + abs(0.0 - 0.0)
        self.assertAlmostEqual(self.similarity(state), expected)

    def test_no_facts(self):
        state = DummyState(set())
        expected = abs(0.0 - 0.2) + abs(0.0 - 1.0) + abs(0.0 - 0.0)
        self.assertAlmostEqual(self.similarity(state), expected)

if __name__ == "__main__":
    unittest.main()
