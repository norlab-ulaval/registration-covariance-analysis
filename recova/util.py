#!/usr/bin/env python3

import numpy as np
import subprocess
import sys

POSITIVE_STRINGS = ('yes', 'y', 't', 'true', '1')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def empty_to_none(dictionary):
    return dictionary if dictionary else None

def parse_dims(dim_string):
    """
    Parse a string containing a list of dimensions to use when plotting.
    """
    dims = [int(x.strip()) for x in dim_string.split(',')]
    if len(dims) != 3:
        raise RuntimeError('Can only generate an ellipsoid with 3 dimensions.')

    return dims

def run_subprocess(command_string, input=None):
    return subprocess.check_output(
        command_string,
        input=input,
        universal_newlines=True,
        shell=True
    )

def nearestPD(A):
    """Find the nearest positive-definite matrix to input

    A Python/Numpy port of John D'Errico's `nearestSPD` MATLAB code [1], which
    credits [2].

    [1] https://www.mathworks.com/matlabcentral/fileexchange/42885-nearestspd

    [2] N.J. Higham, "Computing a nearest symmetric positive semidefinite
    matrix" (1988): https://doi.org/10.1016/0024-3795(88)90223-6
    """

    B = (A + A.T) / 2
    _, s, V = np.linalg.svd(B)

    H = np.dot(V.T, np.dot(np.diag(s), V))

    A2 = (B + H) / 2

    A3 = (A2 + A2.T) / 2

    if isPD(A3):
        return A3

    spacing = np.spacing(np.linalg.norm(A))
    # The above is different from [1]. It appears that MATLAB's `chol` Cholesky
    # decomposition will accept matrixes with exactly 0-eigenvalue, whereas
    # Numpy's will not. So where [1] uses `eps(mineig)` (where `eps` is Matlab
    # for `np.spacing`), we use the above definition. CAVEAT: our `spacing`
    # will be much larger than [1]'s `eps(mineig)`, since `mineig` is usually on
    # the order of 1e-16, and `eps(1e-16)` is on the order of 1e-34, whereas
    # `spacing` will, for Gaussian random matrixes of small dimension, be on
    # othe order of 1e-16. In practice, both ways converge, as the unit test
    # below suggests.
    I = np.eye(A.shape[0])
    k = 1
    while not isPD(A3):
        mineig = np.min(np.real(np.linalg.eigvals(A3)))
        A3 += I * (-mineig * k**2 + spacing)
        k += 1

    error = np.linalg.norm(A - A3)
    if error > 1e-6:
        eprint('Warning: high reconstruction error detected when correcting a Positive Definite matrix. {}'.format(error))

    return A3

def isPD(B):
    """Returns true when input is positive-definite, via Cholesky"""
    try:
        _ = np.linalg.cholesky(B)
        return True
    except np.linalg.LinAlgError:
        return False
