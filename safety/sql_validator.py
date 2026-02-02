FORBIDDEN = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER"]

def validate_sql(sql: str):
    sql_upper = sql.upper()
    for word in FORBIDDEN:
        if word in sql_upper:
            raise ValueError("Forbidden SQL operation detected")
