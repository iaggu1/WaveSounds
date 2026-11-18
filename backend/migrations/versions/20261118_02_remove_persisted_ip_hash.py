from alembic import op

revision = "20261118_02"
down_revision = "20261118_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE leads DROP COLUMN IF EXISTS ip_hash")


def downgrade() -> None:
    op.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS ip_hash VARCHAR(64)")

