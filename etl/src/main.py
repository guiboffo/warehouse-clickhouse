import sys
from jobs.users import run_users
from jobs.organizations import run_organizations
from jobs.projects import run_projects


USAGE = """
Usage:
  python /app/src/main.py users
  python /app/src/main.py organizations
  python /app/src/main.py projects
  python /app/src/main.py all
"""

def main():
    if len(sys.argv) < 2:
        print(USAGE.strip())
        sys.exit(1)

    job = sys.argv[1].strip().lower()

    if job == "users":
        run_users()
        return

    if job == "organizations":
        run_organizations()
        return

    if job == "projects":
        run_projects()
        return

    if job == "all":
        run_organizations()
        run_users()
        run_projects()
        return

    print(f"Unknown job: {job}")
    print(USAGE.strip())
    sys.exit(1)

if __name__ == "__main__":
    main()
