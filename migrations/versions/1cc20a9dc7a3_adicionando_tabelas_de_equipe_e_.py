"""Adicionando tabelas de Equipe e Avaliação

Revision ID: 1cc20a9dc7a3
Revises: 
Create Date: 2024-09-04 21:12:34.338202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cc20a9dc7a3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('equipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tarefa',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('complexidade', sa.Integer(), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('atividade_equipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('equipe_id', sa.Integer(), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('data_atividade', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['equipe_id'], ['equipe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('avaliacao_equipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('equipe_id', sa.Integer(), nullable=False),
    sa.Column('projeto_id', sa.Integer(), nullable=False),
    sa.Column('avaliador', sa.String(length=100), nullable=False),
    sa.Column('data_avaliacao', sa.DateTime(), nullable=False),
    sa.Column('nota', sa.Float(), nullable=False),
    sa.Column('comentarios', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['equipe_id'], ['equipe.id'], ),
    sa.ForeignKeyConstraint(['projeto_id'], ['projeto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('equipe_membros',
    sa.Column('equipe_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['equipe_id'], ['equipe.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('equipe_id', 'usuario_id')
    )
    op.create_table('fase_projeto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descricao', sa.String(length=200), nullable=False),
    sa.Column('percentual', sa.Float(), nullable=False),
    sa.Column('completada', sa.Boolean(), nullable=True),
    sa.Column('projeto_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['projeto_id'], ['projeto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('hipotese')
    op.drop_table('questao')
    op.drop_table('possibilidade_solucao')
    op.drop_table('problema')
    op.drop_table('grande_area')
    with op.batch_alter_table('projeto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nivel_atual', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recursos_necessarios', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('recursos_manutencao', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projeto', schema=None) as batch_op:
        batch_op.drop_column('recursos_manutencao')
        batch_op.drop_column('recursos_necessarios')
        batch_op.drop_column('nivel_atual')

    op.create_table('grande_area',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('nome', sa.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('problema',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('grande_area_id', sa.INTEGER(), nullable=True),
    sa.Column('descricao', sa.TEXT(), nullable=False),
    sa.Column('impacto', sa.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['grande_area_id'], ['grande_area.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('possibilidade_solucao',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('problema_id', sa.INTEGER(), nullable=True),
    sa.Column('descricao', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['problema_id'], ['problema.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questao',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('grande_area_id', sa.INTEGER(), nullable=True),
    sa.Column('descricao', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['grande_area_id'], ['grande_area.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hipotese',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('grande_area_id', sa.INTEGER(), nullable=True),
    sa.Column('descricao', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['grande_area_id'], ['grande_area.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('fase_projeto')
    op.drop_table('equipe_membros')
    op.drop_table('avaliacao_equipe')
    op.drop_table('atividade_equipe')
    op.drop_table('tarefa')
    op.drop_table('equipe')
    # ### end Alembic commands ###
