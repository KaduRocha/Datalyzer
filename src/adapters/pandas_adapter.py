# adapters/pandas_adapter.py
import pandas as pd

class PandasAdapter:
    def read(self, source):
        return pd.read_csv(source)

    def count(self, df):
        return len(df)