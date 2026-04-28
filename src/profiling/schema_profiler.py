# src/profiling/schema_profiler.py

class SchemaProfiler:

    def __init__(self, connector):
        self.conn = connector

    def get_schemas(self):
        sql = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
        """
        return self.conn.query(sql)

    def get_tables(self):
        sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        AND table_schema NOT IN ('pg_catalog', 'information_schema')
        """
        return self.conn.query(sql)

    def get_columns(self):
        sql = """
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        """
        return self.conn.query(sql)

    def get_primary_keys(self):
        sql = """
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
        """
        return self.conn.query(sql)

    def get_foreign_keys(self):
        sql = """
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        """
        return self.conn.query(sql)

    def get_indexes(self):
        sql = """
        SELECT
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        """
        return self.conn.query(sql)

    def run_full_profile(self):
        return {
            "schemas": self.get_schemas(),
            "tables": self.get_tables(),
            "columns": self.get_columns(),
            "primary_keys": self.get_primary_keys(),
            "foreign_keys": self.get_foreign_keys(),
            "indexes": self.get_indexes()
        }