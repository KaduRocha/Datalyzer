# # src/core/engine.py

# class DataEngine:

#     def __init__(self, adapter):
#         self.adapter = adapter

#     def run_profiling(self, source):
#         df = self.adapter.read(source)

#         profile = {
#             "rows": self.adapter.count(df),
#             # expandir depois
#         }

#         return profile


# src/core/engine.py

# from connectors.postgres import PostgresConnector
from src.connectors.postgres import PostgresConnector
from profiling.schema_profiler import SchemaProfiler


class DataEngine:

    def __init__(self, config):
        self.config = config

    def run_schema_profile(self):
        conn = PostgresConnector(**self.config)

        profiler = SchemaProfiler(conn)
        result = profiler.run_full_profile()

        conn.close()

        return result