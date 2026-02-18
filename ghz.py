import math
from bloqade import qasm2
from circuit import Circuit
from gates import h, cx


class GHZ(Circuit):
    @classmethod
    def linear_depth(cls, num_qubits):
        @qasm2.extended
        def kernel(qreg, creg):
            h(qreg, 0)
            for i in range(num_qubits - 1):
                cx(qreg, i, i + 1)

        return cls(kernel=kernel, num_qubits=num_qubits)

    @classmethod
    def log_depth(cls, num_qubits):
        s = math.ceil(math.log2(num_qubits))

        @qasm2.extended
        def kernel(qreg, creg):
            h(qreg, 0)
            for m in range(s, 0, -1):
                step = 2**m
                half = 2 ** (m - 1)
                for k in range(0, num_qubits, step):
                    if k + half < num_qubits:
                        cx(qreg, k, k + half)

        return cls(kernel=kernel, num_qubits=num_qubits)
