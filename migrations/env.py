import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')  # 프로젝트 루트 경로 추가
from app import app  # Flask 애플리케이션 가져오기

from alembic import context  # Alembic context 가져오기
from flask_migrate import Migrate
from app import db

config = context.config  # Alembic config 객체 정의

from flask import current_app

def get_engine():
    with app.app_context():
        try:
            # this works with Flask-SQLAlchemy<3 and Alchemical
            return current_app.extensions['migrate'].db.get_engine()
        except (TypeError, AttributeError):
            # this works with Flask-SQLAlchemy>=3
            return current_app.extensions['migrate'].db.engine


with app.app_context():
    target_db = db  # SQLAlchemy 인스턴스 직접 참조
    migrate = Migrate(app, target_db)  # Flask-Migrate 초기화
    config.set_main_option('sqlalchemy.url', get_engine().url.render_as_string(hide_password=False).replace('%', '%%'))

import logging
from logging.config import fileConfig

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    with app.app_context():
        conf_args = current_app.extensions['migrate'].configure_args
        if conf_args.get("process_revision_directives") is None:
            conf_args["process_revision_directives"] = process_revision_directives

        connectable = get_engine()

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                **conf_args
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
