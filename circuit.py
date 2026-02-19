from bloqade import squin
from bloqade.pyqrack import StackMemorySimulator


class Circuit:
    def __init__(self, kernel, num_qubits):
        self.kernel = kernel
        self.num_qubits = num_qubits

    @staticmethod
    def _get_probs(result):
        return {
            "".join(str(bit.value) for bit in bitstr): prob
            for bitstr, prob in result.items()
        }

    def measure_z_basis(self, num_shots):
        @squin.kernel
        def kernel():
            qreg = squin.qalloc(self.num_qubits)
            self.kernel(qreg)
            return squin.broadcast.measure(qreg)

        sim = StackMemorySimulator(min_qubits=self.num_qubits)
        res = sim.task(kernel=kernel).batch_run(shots=num_shots)
        probs = self._get_probs(result=res)
        return probs

    def measure_x_basis(self, num_shots):
        @squin.kernel
        def kernel():
            qreg = squin.qalloc(self.num_qubits)
            self.kernel(qreg)
            squin.broadcast.h(qreg)
            return squin.broadcast.measure(qreg)

        sim = StackMemorySimulator(min_qubits=self.num_qubits)
        res = sim.task(kernel=kernel).batch_run(shots=num_shots)
        probs = self._get_probs(result=res)
        return probs
