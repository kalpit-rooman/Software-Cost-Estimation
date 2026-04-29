import json, sys, traceback
import pandas as pd
from src.cv_pipeline import run_full_benchmark, save_benchmark_artifacts
try:
    results = run_full_benchmark(training_epochs=100, tuning_epochs=30, n_particles=15, iters=25, verbose=0)
    paths = save_benchmark_artifacts(results)
    print('BENCHMARK_STATUS=SUCCESS')
    print('SAVED_PATHS_JSON=' + json.dumps({k: str(v) for k, v in paths.items()}, sort_keys=True))
    holdout = pd.read_csv(paths['holdout_results'])
    print('HOLDOUT_ROWS_START')
    print(holdout[['Dataset','Model','RMSE']].to_csv(index=False).strip())
    print('HOLDOUT_ROWS_END')
    comparison = pd.read_csv(paths['full_comparison_final'])
    cols = [c for c in ['Dataset','Model','RMSE_mean','RMSE_std'] if c in comparison.columns]
    print('COMPARISON_ROWS_START')
    print(comparison[cols].to_csv(index=False).strip())
    print('COMPARISON_ROWS_END')
except Exception as exc:
    print('BENCHMARK_STATUS=ERROR')
    for frame in traceback.extract_tb(exc.__traceback__):
        print(f'FRAME file={frame.filename} line={frame.lineno} func={frame.name}')
        print(f'CODE {frame.line}')
    print('TRACEBACK_START')
    traceback.print_exc()
    print('TRACEBACK_END')
    sys.exit(1)
