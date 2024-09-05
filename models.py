from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    fases = db.relationship('FaseProjeto', backref='projeto', lazy=True)

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
    historico = db.Column(db.Text)  # Armazenado como uma string JSON

# Modelo de Habilidade
class Habilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    complexidade = db.Column(db.Integer, nullable=False)  # Nível de complexidade
    valor = db.Column(db.Integer, nullable=False)  # Valor da tarefa baseado na complexidade

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
