"""Criando tabelas iniciais

Revision ID: 211fc484a0bb
Revises: 1cc20a9dc7a3
Create Date: 2024-09-04 23:58:30.339376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '211fc484a0bb'
down_revision = '1cc20a9dc7a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projeto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contribuicao_financeira', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('contribuicao_trabalho', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projeto', schema=None) as batch_op:
        batch_op.drop_column('contribuicao_trabalho')
        batch_op.drop_column('contribuicao_financeira')

    # ### end Alembic commands ###
