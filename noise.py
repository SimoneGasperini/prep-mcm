from dataclasses import dataclass, field

from bloqade import squin
from bloqade.cirq_utils.noise import GeminiOneZoneNoiseModel
from bloqade.cirq_utils.noise.model import GeminiNoiseModelABC
from bloqade.rewrite.passes import AggressiveUnroll

from kirin.rewrite.abc import RewriteRule, RewriteResult
from kirin.rewrite import Walk
from kirin.passes import Pass
from kirin.dialects import py, ilist
from kirin import ir


@dataclass
class NoiseInjectionRule(RewriteRule):
    noise_model: GeminiNoiseModelABC = field(default_factory=GeminiOneZoneNoiseModel)

    def rewrite_Statement(self, node: ir.Statement) -> RewriteResult:
        match node:
            case squin.gate.stmts.SingleQubitGate() | squin.gate.stmts.RotationGate():
                return self.rewrite_single_qubit_gate(node)
            case squin.gate.stmts.ControlledGate():
                return self.rewrite_controlled_gate(node)
            case _:
                return RewriteResult()

    def rewrite_single_qubit_gate(
        self, node: squin.gate.stmts.SingleQubitGate | squin.gate.stmts.RotationGate
    ) -> RewriteResult:
        # NOTE: add appropriate noise based on custom logic
        p_x, p_y, p_z, p_loss = map(py.Constant, self.noise_model.local_errors)
        noise_stmt = squin.noise.stmts.SingleQubitPauliChannel(
            p_x.result, p_y.result, p_z.result, node.qubits
        )
        loss_stmt = squin.noise.stmts.QubitLoss(p_loss.result, node.qubits)

        # insert statements into the IR; careful with the order here
        loss_stmt.insert_after(noise_stmt)
        noise_stmt.insert_after(node)
        for p in (p_x, p_y, p_z, p_loss):
            p.insert_after(node)

        return RewriteResult(has_done_something=True)

    def rewrite_controlled_gate(
        self, node: squin.gate.stmts.ControlledGate
    ) -> RewriteResult:
        cz_paired_pauli_rates_dict = self.noise_model.cz_paired_error_probabilities
        assert (
            cz_paired_pauli_rates_dict is not None
        )  # is guaranteed by GeminiNoiseModelABC
        paulis = ("I", "X", "Y", "Z")
        cz_paired_rates = [
            py.Constant(cz_paired_pauli_rates_dict[p1 + p2])
            for p1 in paulis
            for p2 in paulis
            if not (p1 == "I" and p2 == "I")
        ]
        paired_rate_list = ilist.New(values=[p.result for p in cz_paired_rates])
        noise_stmt = squin.noise.stmts.TwoQubitPauliChannel(
            paired_rate_list.result, node.controls, node.targets
        )

        noise_stmt.insert_after(node)
        paired_rate_list.insert_after(node)
        for p in cz_paired_rates:
            p.insert_after(node)

        return RewriteResult(has_done_something=True)


@dataclass
class NoisePass(Pass):
    noise_model: GeminiNoiseModelABC = field(default_factory=GeminiOneZoneNoiseModel)

    def unsafe_run(self, mt: ir.Method) -> RewriteResult:
        # NOTE: inline function calls and unroll loops
        result = AggressiveUnroll(self.dialects, no_raise=self.no_raise).fixpoint(mt)

        # actually inject the noise
        result = (
            Walk(NoiseInjectionRule(noise_model=self.noise_model))
            .rewrite(mt.code)
            .join(result)
        )
        return result

    def fixpoint(self, mt: ir.Method, max_iter: int = 32) -> RewriteResult:
        raise NotImplementedError("NoisePass does not support fixpoint iteration")
