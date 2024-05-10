class Gate:
    def __init__(self, func_str: str, input_lst: list):
        self.func = func_str
        self.inputs = input_lst
        self.val = None
        self.loop = False

    def calculate(self, input_lst):
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


def get_data():
    try:
        Q = int(input())
        test_cases = []
        for _ in range(Q):
            gate_dict = {}
            M, N = input().split()
            M = int(M)
            N = int(N)
            for i in range(N):
                inputs = input().split()
                FUNC = inputs[0]
                L = inputs[2:]
                # assert all(val.startswith('O') or val.startswith('O') for val in L[2:]), "Invalid gate inputs"
                gate_dict[f"O{i + 1}"] = Gate(FUNC, L)
            S = int(input())
            input_list = []
            for _ in range(S):
                I = input().split()
                inputs = {index + 1: int(val) for index, val in enumerate(I)}
                input_list.append(inputs)
            output_list = []
            for _ in range(S):
                S_inputs = input().split()
                output_lst = [int(val) for val in S_inputs[1:]]
                output_list.append(output_lst)
            test_cases.append((gate_dict, input_list, output_list))
        return test_cases
    except Exception as e:
        raise RuntimeError(f"Error occurred while getting data: {e}")


def simulate_circuit(gate_dict, input_list, output_list):
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
    except Exception as e:
        raise RuntimeError(f"Error occurred while simulating circuit: {e}")

if __name__ == "__main__":
    try:
        test_cases = get_data()
        for gate_dict, input_list, output_list in test_cases:
            simulate_circuit(gate_dict, input_list, output_list)
    except Exception as e:
        print(f"Error occurred: {e}")
