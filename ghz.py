import math
from bloqade import squin
from circuit import Circuit


class GHZ(Circuit):
    @classmethod
    def linear_depth(cls, num_qubits):
        @squin.kernel
        def kernel(qreg):
            squin.h(qreg[0])
            for i in range(num_qubits - 1):
                squin.cx(qreg[i], qreg[i + 1])

        return cls(kernel=kernel, num_qubits=num_qubits)

    @classmethod
    def log_depth(cls, num_qubits):
        s = math.ceil(math.log2(num_qubits))

        @squin.kernel
        def kernel(qreg):
            squin.h(qreg[0])
            for m in range(s, 0, -1):
                step = 2**m
                half = 2 ** (m - 1)
                for k in range(0, num_qubits, step):
                    if k + half < num_qubits:
                        squin.cx(qreg[k], qreg[k + half])

        return cls(kernel=kernel, num_qubits=num_qubits)

    @classmethod
    def const_depth(cls, num_qubits):
        @squin.kernel
        def kernel(qreg):
            squin.broadcast.h(qreg[0::2])
            squin.broadcast.cx(qreg[0::2], qreg[1::2])
            squin.broadcast.cx(qreg[1 : num_qubits - 1 : 2], qreg[2::2])
            meas = squin.broadcast.measure(qreg[2::2])
            par = 0
            k = 0
            for i in range(2, num_qubits - 1, 2):
                par = par ^ meas[k]
                if par == 1:
                    squin.x(qreg[i + 1])
                k += 1
            squin.broadcast.reset(qreg[2::2])
            squin.broadcast.cx(qreg[1 : num_qubits - 1 : 2], qreg[2::2])

        return cls(kernel=kernel, num_qubits=num_qubits)

    def compute_fidelity(self, num_shots):
        probs_z_basis = self.measure_z_basis(num_shots // 2)
        probs_x_basis = self.measure_x_basis(num_shots // 2)
        zeros = "0" * self.num_qubits
        ones = "1" * self.num_qubits
        p0 = probs_z_basis.get(zeros, 0)
        p1 = probs_z_basis.get(ones, 0)
        xn = sum((-1) ** (b.count("1") % 2) * p for b, p in probs_x_basis.items())
        return (p0 + p1 + xn) / 2
