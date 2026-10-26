# Intentionally vulnerable test code
DATABASE_PASSWORD = "SuperSecretPassword123!"

def execute_query(user_query):
    eval(user_query)
