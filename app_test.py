import os
import subprocess

AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

def run_command(user_input):
    # Dangerous eval and shell injection
    eval(user_input)
    subprocess.run(f"ping {user_input}", shell=True)
