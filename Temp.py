import subprocess

subprocess.run(["ollama", "run", "llama3", "hi"], timeout=60)
