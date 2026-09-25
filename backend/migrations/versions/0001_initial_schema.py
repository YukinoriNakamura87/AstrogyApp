"""Initial client, natal chart cache and per-planet memo tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("birth_time", sa.Time(), nullable=True),
        sa.Column("birth_place", sa.String(255), nullable=False),
        sa.Column("birth_latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("birth_longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("birth_timezone", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "charts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("calculation", postgresql.JSONB(), nullable=False),
        sa.Column("calculation_version", sa.String(50), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("client_id", name="uq_charts_client_id"),
    )
    op.create_table(
        "chart_interpretation_memos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chart_id", sa.Integer(), sa.ForeignKey("charts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("planet", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("chart_id", "planet", name="uq_chart_memos_chart_planet"),
    )


def downgrade() -> None:
    op.drop_table("chart_interpretation_memos")
    op.drop_table("charts")
    op.drop_table("clients")
