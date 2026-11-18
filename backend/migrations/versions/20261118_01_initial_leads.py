from alembic import op

revision = "20261118_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id UUID PRIMARY KEY NOT NULL,
            email VARCHAR(255) NOT NULL,
            plan_interest VARCHAR(32) NOT NULL DEFAULT 'starter',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_leads_email ON leads (email)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS leads")

