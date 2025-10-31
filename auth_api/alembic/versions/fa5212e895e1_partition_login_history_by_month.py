"""create partitioned login_history table

Revision ID: fa5212e895e1
Revises: f1960c065295
Create Date: 2025-07-26 14:03:28.643353
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa5212e895e1'
down_revision = '7dab07183afb'
branch_labels = None
depends_on = None


def upgrade():
    # Удалим если существует старая таблица
    op.execute("DROP TABLE IF EXISTS login_history CASCADE;")

    # Создание основной таблицы с партиционированием по login_time
    op.execute("""
        CREATE TABLE login_history (
            id SERIAL,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            ip_address VARCHAR,
            user_agent VARCHAR,
            login_time TIMESTAMP NOT NULL DEFAULT now(),
            PRIMARY KEY (id, login_time)
        ) PARTITION BY RANGE (login_time);
    """)

    # Создание партиций на 5 месяцев вперёд
    op.execute("""
        CREATE TABLE login_history_2025_07 PARTITION OF login_history
        FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
    """)
    op.execute("""
        CREATE TABLE login_history_2025_08 PARTITION OF login_history
        FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
    """)
    op.execute("""
        CREATE TABLE login_history_2025_09 PARTITION OF login_history
        FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
    """)
    op.execute("""
        CREATE TABLE login_history_2025_10 PARTITION OF login_history
        FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
    """)
    op.execute("""
        CREATE TABLE login_history_2025_11 PARTITION OF login_history
        FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS login_history_2025_11 CASCADE;")
    op.execute("DROP TABLE IF EXISTS login_history_2025_10 CASCADE;")
    op.execute("DROP TABLE IF EXISTS login_history_2025_09 CASCADE;")
    op.execute("DROP TABLE IF EXISTS login_history_2025_08 CASCADE;")
    op.execute("DROP TABLE IF EXISTS login_history_2025_07 CASCADE;")
    op.execute("DROP TABLE IF EXISTS login_history CASCADE;")
