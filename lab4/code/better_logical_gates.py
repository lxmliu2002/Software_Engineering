"""
Module: better_logical_gates.py
Description: Contains classes and functions for simulating logical gates
"""

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
        except Exception as exc:
            raise RuntimeError(f"Error occurred while calculating {self.func}: {exc}") from exc

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
        except Exception as exc:
            raise RuntimeError(f"Error occurred while solving: {exc}") from exc

    def clear(self):
        """Clears the output value of the gate."""
        self.val = None


def get_data():
    """
    Retrieves test case data from input.

    Returns:
        list: List of test cases.
    """
    try:
        q = int(input())
        test_cases = []
        for _ in range(q):
            gate_dict = {}
            _, n = map(int, input().split())
            for i in range(n):
                inputs = input().split()
                func = inputs[0]
                l = inputs[2:]
                # assert all(val.startswith('O') or val.startswith('O') for val in l[2:]), "Invalid gate inputs"
                gate_dict[f"O{i + 1}"] = Gate(func, l)
            s = int(input())
            input_list = []
            for _ in range(s):
                i = input().split()
                inputs = {index + 1: int(val) for index, val in enumerate(i)}
                input_list.append(inputs)
            output_list = []
            for _ in range(s):
                s_inputs = input().split()
                output_lst = [int(val) for val in s_inputs[1:]]
                output_list.append(output_lst)
            test_cases.append((gate_dict, input_list, output_list))
        return test_cases
    except Exception as exc:
        raise RuntimeError(f"Error occurred while getting data: {exc}") from exc


def simulate_circuit(gate_dict, input_list, output_list):
    """
    Simulates the logic circuit.

    Args:
        gate_dict (dict): Dictionary containing gate instances.
        input_list (list): List of input values.
        output_list (list): List of expected output values.
    """
    try:
        for inputs, expected_output in zip(input_list, output_list):
            is_loop = False
            for gate in gate_dict.values():
                gate.clear()
            for j in range(1, len(gate_dict) + 1):
                gate_dict[f"O{j}"].solve(gate_dict, inputs, set())
                if gate_dict[f"O{j}"].loop:
                    is_loop = True
                    break
            if is_loop:
                print("LOOP")
                break
            for output_index in expected_output:
                print(gate_dict[f"O{output_index}"].val, end=' ')
            print("")
    except Exception as exc:
        raise RuntimeError(f"Error occurred while simulating circuit: {exc}") from exc


if __name__ == "__main__":
    try:
        test_cases = get_data()
        for gate_dict, input_list, output_list in test_cases:
            simulate_circuit(gate_dict, input_list, output_list)
    except Exception as exc:
        print(f"Error occurred: {exc}")
