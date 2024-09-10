from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabela associativa para usuários e tarefas
usuarios_tarefas = db.Table('usuarios_tarefas',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('tarefa_id', db.Integer, db.ForeignKey('tarefa.id'), primary_key=True)
)

# Modelo de Projeto
class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    equipe = db.Column(db.String(200))
    status = db.Column(db.String(50), nullable=False)
    comentarios = db.Column(db.Text)
    prazo_revisao = db.Column(db.String(50))
    recursos_aprovados = db.Column(db.Integer, default=0)
    nivel_atual = db.Column(db.Integer, default=1)  # Nível do projeto (1, 2, 3)
    recursos_necessarios = db.Column(db.Integer, nullable=False)  # Total de recursos necessários
    recursos_manutencao = db.Column(db.Integer, default=0)  # Recursos para manutenção
    
    # Campo para armazenar sugestões de problemas relacionados ao projeto
    sugestao_problema = db.Column(db.String(255), nullable=False)

    # Campo para rastrear tarefas completadas
    tarefas_completadas = db.Column(db.Integer, default=0)  # Contagem de tarefas completadas

    # Novos campos:
    contribuicao_financeira = db.Column(db.Float, default=0)  # Contribuição financeira
    contribuicao_trabalho = db.Column(db.Float, default=0)  # Contribuição de trabalho

    # Relacionamentos com Grandes Áreas, Hipóteses e Questões
    grande_area_id = db.Column(db.Integer, db.ForeignKey('grande_area.id'))
    hipotese_id = db.Column(db.Integer, db.ForeignKey('hipotese.id'))
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'))

    # Relacionamento com Grande Problema
    grande_problema_id = db.Column(db.Integer, db.ForeignKey('grande_problema.id'), nullable=True)

    # Relacionamentos adicionais:
    fases = db.relationship('FaseProjeto', backref='projeto', lazy=True)
    transacoes = db.relationship('Transacao', backref='projeto_rel', lazy=True)
    tarefas = db.relationship('Tarefa', backref='projeto', lazy=True)  # Relacionamento com tarefas

    # Métodos para calcular progresso financeiro e de trabalho
    def calcular_progresso_financeiro(self):
        return (self.contribuicao_financeira / self.recursos_necessarios) * 100 if self.recursos_necessarios else 0

    def calcular_progresso_trabalho(self):
        total_trabalho_necessario = sum(fase.percentual for fase in self.fases)
        return (self.contribuicao_trabalho / total_trabalho_necessario) * 100 if total_trabalho_necessario else 0


# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    complexidade = db.Column(db.Integer, nullable=False)  # Nível de complexidade
    valor = db.Column(db.Integer, nullable=False)  # Valor da tarefa em moedas
    completada = db.Column(db.Boolean, default=False)  # Status de conclusão
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'))  # Ligação com o projeto
    usuarios = db.relationship('Usuario', secondary=usuarios_tarefas, backref='tarefas')  # Relacionamento com usuários


# Modelo de Transação
class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'))
    tipo = db.Column(db.String(50), nullable=False)  # 'virtual' ou 'real'
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='transacoes')
    projeto = db.relationship('Projeto', backref=db.backref('transacoes_projeto', lazy=True))


# Modelo de Grande Problema
class GrandeProblema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    projetos = db.relationship('Projeto', backref='grande_problema', lazy=True)


# Modelo de Fase do Projeto
class FaseProjeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    percentual = db.Column(db.Float, nullable=False)  # Percentual de recursos para a fase
    completada = db.Column(db.Boolean, default=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)


# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    habilidades = db.Column(db.Text)  # Armazenado como uma string separada por vírgulas
    nivel = db.Column(db.String(50), nullable=False)
    formacao = db.Column(db.String(100), nullable=True)  # Grau de formação
    instituicao = db.Column(db.String(100), nullable=True)  # Instituição de formação
    vinculo = db.Column(db.String(100), nullable=True)  # Vínculo atual
    especialidades = db.Column(db.Text, nullable=True)  # Múltiplas especialidades
    historico = db.Column(db.Text)  # Armazenado como uma string JSON


# Modelo de Habilidade
class Habilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Modelo de Equipe
class Equipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    membros = db.relationship('Usuario', secondary='equipe_membros', backref='equipes')

# Tabela associativa para usuários em equipes
equipe_membros = db.Table('equipe_membros',
    db.Column('equipe_id', db.Integer, db.ForeignKey('equipe.id'), primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
)

# Modelo de Avaliação da Equipe
class AvaliacaoEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    avaliador = db.Column(db.String(100), nullable=False)  # Nome do avaliador
    data_avaliacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nota = db.Column(db.Float, nullable=False)  # Nota de 0 a 10
    comentarios = db.Column(db.Text)

    equipe = db.relationship('Equipe', backref=db.backref('avaliacoes', lazy=True))
    projeto = db.relationship('Projeto', backref=db.backref('avaliacoes', lazy=True))

# Modelo de Atividade da Equipe
class AtividadeEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_atividade = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    equipe = db.relationship('Equipe', backref=db.backref('atividades', lazy=True))


# Modelo de Grande Área
class GrandeArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    projetos = db.relationship('Projeto', backref='grande_area', lazy=True)

# Modelo de Hipótese
class Hipotese(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    projetos = db.relationship('Projeto', backref='hipotese', lazy=True)

# Modelo de Questão
class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    projetos = db.relationship('Projeto', backref='questao', lazy=True)

# Modelo de Mensagem
class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

    remetente = db.relationship('Usuario', foreign_keys=[remetente_id], backref='mensagens_enviadas')
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id], backref='mensagens_recebidas')

# Modelo de Fórum
class Forum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    criador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    criador = db.relationship('Usuario', backref='foruns_criados')

# Modelo de Feedback
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'))
    auditor = db.Column(db.String(100))
    conteudo = db.Column(db.Text, nullable=False)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)

    projeto = db.relationship('Projeto', backref='feedbacks')
