from __future__ import annotations

import random
from collections.abc import Iterator
from contextlib import contextmanager

import numpy as np


@contextmanager
def temporary_random_seed(seed: int) -> Iterator[None]:
    random_state = random.getstate()
    numpy_state = np.random.get_state()
    try:
        random.seed(seed)
        np.random.seed(seed)
        yield
    finally:
        random.setstate(random_state)
        np.random.set_state(numpy_state)
