import pandas as pd

from Backend.algorithm.pipeline import run_pipeline


market_cap_df = pd.read_csv(
    "sample_data/market_cap/2026-01-01.csv"
)

volume_df = pd.read_csv(
    "sample_data/trading_volume/2026-01-01.csv"
)


result = run_pipeline(
    market_cap_df,
    volume_df,
)


print("\n========== PIPELINE RESULT ==========\n")

print(result)