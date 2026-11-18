from alembic import op

revision = "20261118_03"
down_revision = "20261118_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE email_outbox (
            id UUID PRIMARY KEY NOT NULL,
            lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
            event_type VARCHAR(32) NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            locked_until TIMESTAMPTZ NULL,
            last_error_code VARCHAR(64) NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_email_outbox_lead_event UNIQUE (lead_id, event_type),
            CONSTRAINT ck_email_outbox_status CHECK (status IN ('pending', 'processing', 'failed')),
            CONSTRAINT ck_email_outbox_attempts CHECK (attempts >= 0)
        )
        """
    )
    op.execute("CREATE INDEX ix_email_outbox_due ON email_outbox (status, available_at, locked_until)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS email_outbox")

