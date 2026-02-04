revision = "20260204_01_schema"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    with op.batch_alter_table("produtos") as batch:
        batch.add_column(sa.Column("nome_normalizado", sa.String(length=220)))
    op.execute("UPDATE produtos SET nome_normalizado = lower(nome)")
    with op.batch_alter_table("materias_primas") as batch:
        batch.add_column(sa.Column("nome_normalizado", sa.String(length=220)))
    op.execute("UPDATE materias_primas SET nome_normalizado = lower(nome)")

def downgrade() -> None:
    with op.batch_alter_table("produtos") as batch:
        batch.drop_column("nome_normalizado")
    with op.batch_alter_table("materias_primas") as batch:
        batch.drop_column("nome_normalizado")
