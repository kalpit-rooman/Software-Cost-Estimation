from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ensemble import DEFAULT_ENSEMBLE_SEEDS
from src.cv_pipeline import run_full_benchmark, save_benchmark_artifacts


def parse_args() -> argparse.Namespace:
    """Parse runtime overrides for the benchmark budget."""
    parser = argparse.ArgumentParser(description="Run the clean benchmark pipeline.")
    parser.add_argument("--training-epochs", type=int, default=100)
    parser.add_argument("--tuning-epochs", type=int, default=30)
    parser.add_argument("--n-particles", type=int, default=15)
    parser.add_argument("--iters", type=int, default=25)
    parser.add_argument("--ensemble-size", type=int, default=len(DEFAULT_ENSEMBLE_SEEDS))
    parser.add_argument("--ensemble-epochs", type=int, default=200)
    parser.add_argument("--verbose", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    """Run the clean benchmark pipeline and print the saved artifacts."""
    args = parse_args()
    if args.ensemble_size < 1 or args.ensemble_size > len(DEFAULT_ENSEMBLE_SEEDS):
        raise ValueError(f"ensemble-size must be between 1 and {len(DEFAULT_ENSEMBLE_SEEDS)}")

    results = run_full_benchmark(
        training_epochs=args.training_epochs,
        tuning_epochs=args.tuning_epochs,
        n_particles=args.n_particles,
        iters=args.iters,
        ensemble_seeds=DEFAULT_ENSEMBLE_SEEDS[: args.ensemble_size],
        ensemble_epochs=args.ensemble_epochs,
        verbose=args.verbose,
    )
    saved_paths = save_benchmark_artifacts(results)

    print("SAVED_PATHS")
    for key, path in saved_paths.items():
        print(f"{key}={path}")

    print("HOLDOUT_RESULTS")
    print(results["holdout_results"].to_csv(index=False))

    print("FULL_COMPARISON_FINAL")
    print(results["full_comparison_final"].to_csv(index=False))


if __name__ == "__main__":
    main()