from __future__ import annotations

from typing import Callable, Dict, Tuple

import numpy as np


def tune_cnn_with_pso(
	objective_fn: Callable[[np.ndarray], np.ndarray],
	dimensions: int,
	lower_bounds: np.ndarray,
	upper_bounds: np.ndarray,
	n_particles: int = 10,
	iters: int = 20,
	options: Dict[str, float] | None = None,
) -> Tuple[float, np.ndarray]:
	"""Run global-best PSO and return best score and best hyperparameter vector."""
	try:
		import pyswarms as ps
	except ImportError as exc:
		raise ImportError("pyswarms is required for PSO tuning") from exc

	if options is None:
		options = {"c1": 0.5, "c2": 0.3, "w": 0.9}

	optimizer = ps.single.GlobalBestPSO(
		n_particles=n_particles,
		dimensions=dimensions,
		options=options,
		bounds=(lower_bounds, upper_bounds),
	)

	best_cost, best_position = optimizer.optimize(objective_fn, iters=iters)
	return float(best_cost), best_position


def decode_cnn_hyperparameters(position: np.ndarray) -> Dict[str, float | int]:
	"""Map a PSO position vector to typed CNN hyperparameters."""
	filters = int(np.clip(round(position[0]), 8, 128))
	kernel_size = int(np.clip(round(position[1]), 2, 7))
	dense_units = int(np.clip(round(position[2]), 8, 256))
	learning_rate = float(np.clip(position[3], 1e-4, 1e-2))

	return {
		"filters": filters,
		"kernel_size": kernel_size,
		"dense_units": dense_units,
		"learning_rate": learning_rate,
	}
