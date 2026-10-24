"""Operational commands.

    python -m app.cli migrate            # alembic upgrade head
    python -m app.cli seed               # repeatable demo seed (refuses in production)
    python -m app.cli reset-demo --yes   # drop + migrate + seed (refuses in production)
    python -m app.cli worker [--once]    # background jobs
    python -m app.cli create-admin --email you@org   # password read from ADMIN_PASSWORD env var
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from alembic import command
from alembic.config import Config


def _alembic_cfg() -> Config:
    return Config(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "alembic.ini"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate")
    sub.add_parser("seed")
    reset = sub.add_parser("reset-demo")
    reset.add_argument("--yes", action="store_true", help="confirm destroying all data in the dev database")
    worker = sub.add_parser("worker")
    worker.add_argument("--once", action="store_true")
    admin = sub.add_parser("create-admin")
    admin.add_argument("--email", required=True)
    admin.add_argument("--name", default="System Administrator")
    args = parser.parse_args(argv)

    from app.core.config import get_settings
    from app.core.logging import configure_logging

    configure_logging()
    settings = get_settings()

    if args.cmd == "migrate":
        command.upgrade(_alembic_cfg(), "head")
        return 0

    from app.db.session import get_engine, session_factory

    if args.cmd == "seed":
        from app import seed

        with session_factory()() as db:
            print(json.dumps(seed.run(db)))
        return 0

    if args.cmd == "reset-demo":
        if settings.is_production:
            print("Refusing to reset data in production", file=sys.stderr)
            return 2
        if not args.yes:
            print("Pass --yes to confirm dropping all data", file=sys.stderr)
            return 2
        from sqlalchemy import text

        from app import seed
        from app.db.base import Base

        engine = get_engine()
        Base.metadata.drop_all(engine)
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        command.upgrade(_alembic_cfg(), "head")
        with session_factory()() as db:
            print(json.dumps(seed.run(db)))
        return 0

    if args.cmd == "worker":
        from app.jobs import worker as w

        if args.once:
            print(json.dumps(w.run_once(session_factory()), default=str))
        else:
            w.run_forever(session_factory())
        return 0

    if args.cmd == "create-admin":
        password = os.environ.get("ADMIN_PASSWORD", "")
        if len(password) < 12:
            print("Set ADMIN_PASSWORD (>= 12 chars) in the environment", file=sys.stderr)
            return 2
        from app.core.security import hash_password
        from app.core.time import utcnow
        from app.domain.enums import Role
        from app.models import User, UserRole
        from app.services.auth import normalize_email

        with session_factory()() as db:
            user = User(email=normalize_email(args.email), display_name=args.name,
                        password_hash=hash_password(password))
            user.roles.append(UserRole(role=Role.system_admin, created_at=utcnow()))
            db.add(user)
            db.commit()
            print(json.dumps({"created_user_id": str(user.id)}))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
