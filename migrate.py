#!/usr/bin/env python3
import os
import sys
from alembic.config import Config
from alembic import command

# Get the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/products.db")


def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return alembic_cfg


def init_migrations():
    """Initialize the database with migrations"""
    print("🔧 Initializing database with migrations...")
    alembic_cfg = get_alembic_config()

    try:
        # Run migrations to latest version
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations applied successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def create_migration(message):
    """Create a new migration"""
    print(f"🔧 Creating new migration: {message}")
    alembic_cfg = get_alembic_config()

    try:
        command.revision(alembic_cfg, message=message, autogenerate=True)
        print("✅ Migration created successfully!")
        print("📝 Don't forget to review the migration file before applying it!")
        return True
    except Exception as e:
        print(f"❌ Failed to create migration: {e}")
        return False


def upgrade_to_latest():
    """Upgrade database to latest version"""
    print("🔧 Upgrading database to latest version...")
    alembic_cfg = get_alembic_config()

    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database upgraded successfully!")
        return True
    except Exception as e:
        print(f"❌ Upgrade failed: {e}")
        return False


def downgrade_one():
    """Downgrade database by one version"""
    print("🔧 Downgrading database by one version...")
    alembic_cfg = get_alembic_config()

    try:
        command.downgrade(alembic_cfg, "-1")
        print("✅ Database downgraded successfully!")
        return True
    except Exception as e:
        print(f"❌ Downgrade failed: {e}")
        return False


def show_current():
    """Show current migration version"""
    print("🔧 Current migration version:")
    alembic_cfg = get_alembic_config()

    try:
        command.current(alembic_cfg)
        return True
    except Exception as e:
        print(f"❌ Failed to show current version: {e}")
        return False


def show_history():
    """Show migration history"""
    print("🔧 Migration history:")
    alembic_cfg = get_alembic_config()

    try:
        command.history(alembic_cfg)
        return True
    except Exception as e:
        print(f"❌ Failed to show history: {e}")
        return False


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("""
Database Migration Helper
=========================

Usage:
    python migrate.py init              - Initialize database with migrations
    python migrate.py create "message"  - Create new migration
    python migrate.py upgrade           - Upgrade to latest version
    python migrate.py downgrade         - Downgrade by one version
    python migrate.py current           - Show current version
    python migrate.py history           - Show migration history

Environment Variables:
    DATABASE_URL - Database connection string (default: sqlite:////app/data/products.db)
        """)
        return 1

    command_name = sys.argv[1].lower()

    commands = {
        "init": init_migrations,
        "upgrade": upgrade_to_latest,
        "downgrade": downgrade_one,
        "current": show_current,
        "history": show_history,
    }

    if command_name in commands:
        success = commands[command_name]()
        return 0 if success else 1
    elif command_name == "create":
        if len(sys.argv) < 3:
            print("❌ Error: Migration message required")
            print("Usage: python migrate.py create \"your message here\"")
            return 1
        message = sys.argv[2]
        success = create_migration(message)
        return 0 if success else 1
    else:
        print(f"❌ Unknown command: {command_name}")
        print("Run 'python migrate.py' for usage information")
        return 1


if __name__ == "__main__":
    sys.exit(main())