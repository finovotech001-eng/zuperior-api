import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if "DATABASE_URL" not in os.environ:
    print("Error: DATABASE_URL not found in environment")
    exit(1)

print("DATABASE_URL found, running migration...")

# Run prisma db push
try:
    # On Windows, shell=True is often needed for npx
    result = subprocess.run(
        "npx -y prisma db push --schema schema.prisma", 
        shell=True, 
        check=True,
        capture_output=True,
        text=True
    )
    print("Migration command finished successfully")
    print("Output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Migration failed with return code:", e.returncode)
    print("Stdout:", e.stdout)
    print("Stderr:", e.stderr)
    exit(1)
