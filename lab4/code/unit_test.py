class Gate:
    """
    Represents a logic gate.

    Attributes:
        func (str): The logic function of the gate.
        inputs (list): The list of input ports.
        val (int): The output value of the gate.
        loop (bool): Flag indicating if there is a loop during solving.
    """

    def __init__(self, func_str: str, input_lst: list):
        """
        Initializes a Gate instance.

        Args:
            func_str (str): The logic function string.
            input_lst (list): The list of input ports.
        """
        self.func = func_str
        self.inputs = input_lst
        self.val = None
        self.loop = False

    def calculate(self, input_lst):
        """
        Calculates the output value of the gate.

        Args:
            input_lst (list): The list of input values.
        """
        try:
            operations = {
                "NOT": lambda x: int(not x[0]),
                "AND": lambda x: int(all(x)),
                "OR": lambda x: int(any(x)),
                "XOR": lambda x: int(sum(x) % 2),
                "NAND": lambda x: int(not all(x)),
                "NOR": lambda x: int(not any(x))
            }
            self.val = operations[self.func](input_lst)
        except Exception as e:
            raise RuntimeError(f"Error occurred while calculating {self.func}: {e}")

    def solve(self, gates, inputs, visited):
        """
        Solves the gate.

        Args:
            gates (dict): Dictionary containing gate instances.
            inputs (dict): Dictionary containing input values.
            visited (set): Set containing visited gate names.
        """
        try:
            if self.loop:
                return 0
            tmp_lst = []
            if self.val is None:
                for name in self.inputs:
                    if name in visited:
                        self.loop = True
                        return 0
                    if name[0] == "I":
                        tmp_lst.append(inputs[int(name[1:])])
                    elif name in gates:
                        if gates[name].val is None:
                            visited.add(name)
                            gates[name].solve(gates, inputs, visited)
                            visited.remove(name)
                        if gates[name].val is None:
                            self.loop = True
                            return 0
                        tmp_lst.append(gates[name].val)
                self.calculate(tmp_lst)
            return self.val
        except Exception as e:
            raise RuntimeError(f"Error occurred while solving: {e}")

    def clear(self):
        """Clears the output value of the gate."""
        self.val = None


import unittest

class TestGate(unittest.TestCase):
    def test_calculate(self):
        # Test each logic operation
        gate = Gate("NOT", [0])
        gate.calculate([0])
        self.assertEqual(gate.val, 1)

        gate = Gate("AND", [1, 0, 1])
        gate.calculate([1, 0, 1])
        self.assertEqual(gate.val, 0)

        gate = Gate("OR", [1, 0, 1])
        gate.calculate([1, 0, 1])
        self.assertEqual(gate.val, 1)

        gate = Gate("XOR", [1, 0, 1])
        gate.calculate([1, 0, 1])
        self.assertEqual(gate.val, 0)

        gate = Gate("NAND", [1, 0, 1])
        gate.calculate([1, 0, 1])
        self.assertEqual(gate.val, 1)

        gate = Gate("NOR", [1, 0, 1])
        gate.calculate([1, 0, 1])
        self.assertEqual(gate.val, 0)

        # Test error handling
        gate = Gate("NOT", [0])
        with self.assertRaises(RuntimeError):
            gate.calculate([])  # Empty input list

    def test_solve(self):
        # Test solving logic gates
        gate_dict = {
            "O1": Gate("AND", ["I1", "I2"]),
            "O2": Gate("OR", ["I1", "I3"])
        }
        inputs = {1: 1, 2: 0, 3: 1}
        visited = set()
        gate_dict["O1"].solve(gate_dict, inputs, visited)
        gate_dict["O2"].solve(gate_dict, inputs, visited)
        self.assertEqual(gate_dict["O1"].val, 0)
        self.assertEqual(gate_dict["O2"].val, 1)

        # Test handling loops
        gate_dict = {
            "O1": Gate("AND", ["O2"]),
            "O2": Gate("OR", ["O1"])
        }
        inputs = {}
        visited = set()
        gate_dict["O1"].solve(gate_dict, inputs, visited)
        self.assertTrue(gate_dict["O1"].loop)
        self.assertEqual(gate_dict["O1"].val, None)

    def test_clear(self):
        # Test clearing gate value
        gate = Gate("AND", ["I1", "I2"])
        gate.val = 1
        gate.clear()
        self.assertEqual(gate.val, None)

if __name__ == "__main__":
    unittest.main()
