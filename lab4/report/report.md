# <center>**软件工程实验报告**</center>

<center>Lab4 编程实现、分析和测试</center>

<center> 网络空间安全学院 信息安全专业</center>

<center> 2112492 刘修铭 1027</center>

## 编程实现

本次实验使用 python 进行实现。

首先创建了一个电路门类，为其进行一定的初始化。

```python
class Gate:
    def __init__(self, func_str: str, input_lst: list):
        self.func = func_str
        self.input = input_lst
        self.val = None
        self.loop = False
```

接着按照题目要求，创建了一个 calculate 函数，用于完成门电路的计算。由于题目限定了门电路的种类，基于此插入了错误处理。

```python
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
        print(f"Error occurred while calculating {self.func}: {e}")
```

在本次中，逻辑电路可以看作是一个有向图，其中门（或逻辑门）表示图中的节点，门之间的连接表示有向边，输入端口表示图的起始节点，输出端口表示图的终止节点。在有向图中，如果存在循环，则一定存在一条路径从某个节点出发，经过若干条边回到该节点，这种路径称为循环路径。在逻辑电路中，循环依赖即表示存在循环路径。

通过在逻辑电路中进行深度优先搜索（DFS），可以在图中遍历节点，并在遍历过程中标记已经访问过的节点。如果在遍历过程中发现某个节点已经被标记为已访问过，则说明存在循环依赖，因为在有向图中，节点的访问顺序是由边的方向所决定的，如果已经访问过某个节点，则再次访问该节点必定会回到之前已访问过的节点，形成循环。

solve 函数对门进行深度优先搜索，并使用 loop 属性来标记已经访问过的节点。在遍历过程中，如果发现某个节点已经被访问过，则将该节点的 loop 属性设置为 `True`，表示存在循环依赖，直接返回 0，停止继续计算该节点的值。这样可以确保在计算逻辑电路的值时，不会陷入循环依赖导致的无限递归或死循环，保证了算法的正确性和鲁棒性。

```python
def solve(self, gates, inputs, visited):
    try:
        if self.loop:
            return 0
        tmp_lst = []
        if self.val is None:
            for name in self.input:
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
        print(f"Error occurred while solving: {e}")
        return None
```

然后编写了一个函数用于按照规定格式读入数据，并且设计数据结构进行存储。注意到，题目中提到**<u>“注意 O 序列不一定是递增的，即要求输出的器件可能以任意顺序出现。”</u>**此处对于读入的数据进行处理时，按照题目中的设定，将其输入格式均保存。此处采用 dict 数据类型保存门电路的输入等，采用键值对的形式进行处理，避免了下标越界等问题。

```python
def get_data():
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
```

simulate_circuit 函数基于前面的输入调用函数进行直接计算。

1. 使用 `zip` 函数将 `input_list` 和 `output_list` 中的元素一一对应起来，形成一个迭代器，在每次迭代中得到一组输入值 `inputs` 和对应的期望输出值 `expected_output`。
2. 在每组输入值 `inputs` 上模拟逻辑电路的行为，通过 `gate_dict` 中的门逐一计算其输出值，并与期望输出值进行比较。
3. 在模拟逻辑电路的过程中，如果发现存在环，则输出 "LOOP" 并跳过当前组输入的模拟，进行下一组输入的模拟。
4. 如果不存在环，则将计算得到的输出值依次输出。

```python
def simulate_circuit(gate_dict, input_list, output_list):
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
            continue
        for output_index in expected_output:
            print(gate_dict[f"O{output_index}"].val, end=' ')
        print("")
```

main 主函数中，则调用前面的函数进行综合计算。

运行给定测试样例，可以看到，输出的结果与预期输出相同，说明编程正确。

<img src="./report.pic/image-20240510150640436.png" alt="image-20240510150640436" style="zoom:33%;" />



## 编程规范

> 参考的哪个规范，如何检查是否遵守编程规范的？

本次编程主要参考 [Google 开源项目风格指南](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/contents.html)。

在进行编程规范检查时，使用 ChatGPT 进行检查，得到如下的输出结果。

<img src="./report.pic/image-20240510150858750.png" alt="image-20240510150858750" style="zoom:33%;" />

针对其给出的改进说明，参考 [Google 开源项目风格指南](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/contents.html)，将代码作如下修改。

```python
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

def get_data():
    """
    Retrieves test case data from input.

    Returns:
        list: List of test cases.
    """
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
                continue
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
```

使用 [pylint](https://pypi.org/project/pylint/) 进行原始代码的静态分析，得到如下的结果。

<img src="./report.pic/image-20240510151125639.png" alt="image-20240510151125639" style="zoom:33%;" />

针对于这些问题，将其进行一定的修改，得到如下修改后的代码。

```python
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
        operations = {
            "NOT": lambda x: int(not x[0]),
            "AND": lambda x: int(all(x)),
            "OR": lambda x: int(any(x)),
            "XOR": lambda x: int(sum(x) % 2),
            "NAND": lambda x: int(not all(x)),
            "NOR": lambda x: int(not any(x))
        }
        assert self.func in operations, f"Invalid logic function: {self.func}"
        self.val = operations[self.func](input_lst)

    def solve(self, gates, inputs, visited):
        """
        Solves the gate.

        Args:
            gates (dict): Dictionary containing gate instances.
            inputs (dict): Dictionary containing input values.
            visited (set): Set containing visited gate names.
        """
        if self.loop:
            return 0
        tmp_lst = []
        if self.val is None:
            for name in self.inputs:
                assert name[0] == "I" or name in gates, f"Invalid input: {name}"
                if name[0] == "I":
                    assert int(name[1:]) in inputs, f"Input not provided: {name}"
                    tmp_lst.append(inputs[int(name[1:])])
                else:
                    if gates[name].val is None:
                        assert name not in visited, f"Loop detected: {name}"
                        visited.add(name)
                        gates[name].solve(gates, inputs, visited)
                        visited.remove(name)
                        assert gates[name].val is not None, f"Gate not solved: {name}"
                    tmp_lst.append(gates[name].val)
            self.calculate(tmp_lst)
        return self.val

    def clear(self):
        """Clears the output value of the gate."""
        self.val = None


def get_data():
    """
    Retrieves test case data from input.

    Returns:
        list: List of test cases.
    """
    q = int(input())
    test_cases = []
    for _ in range(q):
        gate_dict = {}
        _, n = map(int, input().split())
        for i in range(n):
            inputs = input().split()
            func = inputs[0]
            l = inputs[2:]
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


def simulate_circuit(gate_dict, input_list, output_list):
    """
    Simulates the logic circuit.

    Args:
        gate_dict (dict): Dictionary containing gate instances.
        input_list (list): List of input values.
        output_list (list): List of expected output values.
    """
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
            continue
        for output_index in expected_output:
            print(gate_dict[f"O{output_index}"].val, end=' ')
        print("")


if __name__ == "__main__":
    cases = get_data()
    for gate_dict, input_list, output_list in cases:
        simulate_circuit(gate_dict, input_list, output_list)

```

对其进行检查，可以看到，所有的问题都已经解决。

<img src="./report.pic/image-20240510154023950.png" alt="image-20240510154023950" style="zoom:50%;" />



## 可扩展性

> 如何提高代码的可扩展性？

对于此编程任务，主要的扩展方向为门电路种类的增加。

本次实验主要有两种拓展思路。

首先，在原始代码中，门电路的实现部分主要在 **calculate** 函数中。即按照门电路要求添加对应的 FUNC 与其计算过程。因此，如果需要扩展，按照要扩展的门电路的要求，对其进行功能与名称的添加即可。

第二种思路则是对现有的代码进行修改，将逻辑门的 calculate 函数和 solve 函数作为接口，并为每种逻辑门创建一个独立的子类。这样做可以轻松地添加新的逻辑门类型，并且使得代码更易于理解和维护。在此给出一个代码示例，不做具体实现。

```python
from abc import ABC, abstractmethod

class LogicGate(ABC):
    """
    Abstract base class for logic gates.
    """
    @abstractmethod
    def calculate(self, input_lst):
        """
        Calculates the output value of the gate.

        Args:
            input_lst (list): The list of input values.
        """
        pass

    @abstractmethod
    def solve(self, gates, inputs, visited):
        """
        Solves the gate.

        Args:
            gates (dict): Dictionary containing gate instances.
            inputs (dict): Dictionary containing input values.
            visited (set): Set containing visited gate names.
        """
        pass

    @abstractmethod
    def clear(self):
        """
        Clears the output value of the gate.
        """
        pass

class NOTGate(LogicGate):
    """
    Represents a NOT logic gate.
    """
    def __init__(self, input_port):
        self.input = input_port
        self.val = None
        self.loop = False

    def calculate(self, input_lst):
        assert len(input_lst) == 1, "NOT gate expects exactly 1 input"
        self.val = int(not input_lst[0])

    def solve(self, gates, inputs, visited):
        if self.loop:
            return 0
        if self.val is None:
            assert self.input in inputs, f"Input not provided: {self.input}"
            self.calculate([inputs[self.input]])
        return self.val

    def clear(self):
        self.val = None

# 添加其他逻辑门的类似实现...

def create_gate(func_str, input_lst):
    """
    Factory function to create logic gates based on function string.

    Args:
        func_str (str): The logic function string.
        input_lst (list): The list of input ports.

    Returns:
        LogicGate: An instance of the appropriate logic gate class.
    """
    if func_str == "NOT":
        assert len(input_lst) == 1, "NOT gate expects exactly 1 input"
        return NOTGate(input_lst[0])
    # 添加其他逻辑门类型的判断和实例化...

```



## 错误与异常处理





## 算法复杂度





## 性能分析与代码优化





## 单元测试

> 测试用例设计思路、测试覆盖指标、覆盖率、测试通过率



https://github.com/richenyunqi/CCF-CSP-and-PAT-solution/blob/master/CCF%20CSP/202009-3.%20%E7%82%B9%E4%BA%AE%E6%95%B0%E5%AD%97%E4%BA%BA%E7%94%9F.md

https://zhuanlan.zhihu.com/p/335516793

https://developer.aliyun.com/article/883777

https://github.com/richenyunqi/CCF-CSP-and-PAT-solution/blob/master/CCF%20CSP/202009-3.%20%E7%82%B9%E4%BA%AE%E6%95%B0%E5%AD%97%E4%BA%BA%E7%94%9F.md

https://github.com/AnyaCoder/CCF-CSP/blob/main/2024-03-12-%E7%82%B9%E4%BA%AE%E6%95%B0%E5%AD%97%E4%BA%BA%E7%94%9F.py

https://github.com/Ya-jiang/CCF-CSP-Question-3/blob/main/%E7%82%B9%E4%BA%AE%E6%95%B0%E5%AD%97%E4%BA%BA%E7%94%9F.cpp

https://github.com/WWaynee/CCF-CSP-code/blob/main/2020-09/%E3%80%9020211104%E3%80%913-%E7%82%B9%E4%BA%AE%E6%95%B0%E5%AD%97%E4%BA%BA%E7%94%9F(100).cpp





https://sim.csp.thusaac.com/contest/20/problem/2
