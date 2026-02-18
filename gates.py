import math
from bloqade import qasm2


@qasm2.extended
def x(qreg, i):
    qasm2.u(qreg[i], math.pi, 0, math.pi)


@qasm2.extended
def x_parallel(qreg):
    qasm2.parallel.u(qreg, math.pi, 0, math.pi)


@qasm2.extended
def y(qreg, i):
    qasm2.u(qreg[i], math.pi, math.pi / 2, math.pi / 2)


@qasm2.extended
def y_parallel(qreg):
    qasm2.parallel.u(qreg, math.pi, math.pi / 2, math.pi / 2)


@qasm2.extended
def z(qreg, i):
    qasm2.u(qreg[i], 0, 0, math.pi)


@qasm2.extended
def z_parallel(qreg):
    qasm2.parallel.u(qreg, 0, 0, math.pi)


@qasm2.extended
def h(qreg, i):
    qasm2.u(qreg[i], math.pi / 2, 0, math.pi)


@qasm2.extended
def h_parallel(qreg):
    qasm2.parallel.u(qreg, math.pi / 2, 0, math.pi)


@qasm2.extended
def s(qreg, i):
    qasm2.u(qreg[i], 0, 0, math.pi / 2)


@qasm2.extended
def s_parallel(qreg):
    qasm2.parallel.u(qreg, 0, 0, math.pi / 2)


@qasm2.extended
def st(qreg, i):
    qasm2.u(qreg[i], 0, 0, -math.pi / 2)


@qasm2.extended
def st_parallel(qreg):
    qasm2.parallel.u(qreg, 0, 0, -math.pi / 2)


@qasm2.extended
def cz(qreg, c, t):
    qasm2.cz(qreg[c], qreg[t])


@qasm2.extended
def cz_parallel(qreg_c, qreg_t):
    qasm2.parallel.cz(qreg_c, qreg_t)


@qasm2.extended
def cx(qreg, c, t):
    h(qreg, t)
    cz(qreg, c, t)
    h(qreg, t)


@qasm2.extended
def cx_parallel(qreg_c, qreg_t):
    h_parallel(qreg_t)
    cz_parallel(qreg_c, qreg_t)
    h_parallel(qreg_t)


@qasm2.extended
def cy(qreg, c, t):
    s(qreg, t)
    cx(qreg, c, t)
    st(qreg, t)


@qasm2.extended
def cy_parallel(qreg_c, qreg_t):
    s_parallel(qreg_t)
    cx_parallel(qreg_c, qreg_t)
    st_parallel(qreg_t)
