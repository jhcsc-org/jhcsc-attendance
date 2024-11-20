import asyncio
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def rollback_migrations():
    """Rollback database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db.py [migrate|rollback]")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "migrate":
        run_migrations()
    elif action == "rollback":
        rollback_migrations()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1) 