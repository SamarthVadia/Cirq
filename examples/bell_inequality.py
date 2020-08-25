"""
Bell's theorem or inequality proves that entanglement based
observations can't be reproduced with any local realist theory [1].

This example shows Bell inequality in form of CHSH game where two
players Alice and Bob receive an input bit x and y respectively and
produce an output a and b based on the input bit.
The goal is to maximize the probability to satisfy the condition [2]:
    a XOR b = x AND y

In the classical deterministic case, the highest probability
achievable is 75%. While with quantum correlations, it can
achieve higher success probability. In the quantum case, two players
Alice and Bob starts with a shared Bell-pair entangled state. The
random input x and y is provided by referee for Alice and Bob. If
the input x (and y) is 0, Alice (Bob) rotates in Y-basis by angle
-pi/16 and if the input is 1, Alice (Bob) rotates by angle 3pi/16.
This is implemented here by a default rotation gate of -pi/16
followed by a custom controlled-rotation gate in Y-basis that 
rotates by angle of pi/4 if input from referee is 1. The success
probability for the above condition will be cos(pi/8)^2 ~ 85.3%

[1] https://en.wikipedia.org/wiki/Bell%27s_theorem
[2] R. de Wolf. Quantum Computing: Lecture Notes (arXiv:1907.09415, Section 15.2)

=== EXAMPLE OUTPUT ===
Circuit:
(0, 0): ───H───@───Z─────────────Ry(-0.062π)───Ry(0.25π)───M('a')───────────────
               │                               │
(0, 1): ───H───┼───────────────────────────────@───────────M('x')───────────────
               │
(1, 0): ───────X───Ry(-0.062π)─────────────────────────────Ry(0.25π)───M('b')───
                                                           │
(1, 1): ───H───────────────────────────────────────────────@───────────M('y')───

Simulating 75 repetitions...

Results
a: 1_1______1_1__1_1__1_1_111____1_1111___1__1_11___1111__1_1_1111______1__1_1
b: 1_1__1_1___1____11_111__1____11111_1___1_11_11_1_____1_11__1_1_1_11__11_1__
x: _1___1_1______11_1__1111_1__111__11___1__1____11_1111__111____11__11_1_1_11
y: ___1_1_111__111_11__1__11111_1_1__1_______111__1_11111_1_1__11_1111__11_1_1
(a XOR b) == (x AND y):
   111111111_111111111111111111111_111111111_11111111111_1__111_1_11_111__1111
Win rate: 85.33333333333333%
"""

import numpy as np

import cirq

class CRy(cirq.TwoQubitGate):

    def __init__(self, theta):
        self.theta = theta

    def _unitary_(self):
            
      sintheta = np.sin(self.theta)
      costheta = np.cos(self.theta)
      
      return np.array([
          [1, 0, 0,               0],
          [0, 1, 0,               0],
          [0, 0, costheta,        -sintheta],
          [0, 0, sintheta,       costheta]
      ])
    
    def _circuit_diagram_info_(self, args):
        # the @ is for control
        return '@', 'Ry({}π)'.format(self.theta / np.pi)
          
          
def main():
    # Create circuit.
    circuit = make_bell_test_circuit()
    print('Circuit:')
    print(circuit)

    # Run simulations.
    print()
    repetitions = 75
    print('Simulating {} repetitions...'.format(repetitions))
    result = cirq.Simulator().run(program=circuit, repetitions=repetitions)

    # Collect results.
    a = np.array(result.measurements['a'][:, 0])
    b = np.array(result.measurements['b'][:, 0])
    x = np.array(result.measurements['x'][:, 0])
    y = np.array(result.measurements['y'][:, 0])
    outcomes = a ^ b == x & y
    win_percent = len([e for e in outcomes if e]) * 100 / repetitions

    # Print data.
    print()
    print('Results')
    print('a:', bitstring(a))
    print('b:', bitstring(b))
    print('x:', bitstring(x))
    print('y:', bitstring(y))
    print('(a XOR b) == (x AND y):\n  ', bitstring(outcomes))
    print('Win rate: {}%'.format(win_percent))


def make_bell_test_circuit():
    alice = cirq.GridQubit(0, 0)
    bob = cirq.GridQubit(1, 0)
    alice_referee = cirq.GridQubit(0, 1)
    bob_referee = cirq.GridQubit(1, 1)

    circuit = cirq.Circuit()

    # Prepare shared entangled state.
    circuit.append([
        cirq.H(alice),
        cirq.CNOT(alice, bob),
        cirq.Z(alice)
    ])

    # Referees flip coins.
    circuit.append([
        cirq.H(alice_referee),
        cirq.H(bob_referee),
    ])

    # Players do a rotation based on the referee's input.
    circuit.append([
        cirq.ry(-np.pi/16)(alice),
        cirq.Circuit(CRy(np.pi/4)(alice_referee, alice)),
        cirq.ry(-np.pi/16)(bob),
        cirq.Circuit(CRy(np.pi/4)(bob_referee, bob)),
    ])

    # Then results are recorded.
    circuit.append([
        cirq.measure(alice, key='a'),
        cirq.measure(bob, key='b'),
        cirq.measure(alice_referee, key='x'),
        cirq.measure(bob_referee, key='y'),
    ])

    return circuit


def bitstring(bits):
    return ''.join('1' if e else '_' for e in bits)


if __name__ == '__main__':
    main()
