from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import (
    db, Usuario, Projeto, Tarefa, Equipe, Habilidade, Feedback, 
    GrandeProblema, FaseProjeto, AvaliacaoEquipe, AtividadeEquipe, 
    Mensagem, Forum, GrandeArea, Hipotese, Questao
)
from seed_data import seed_data
from mensagem import mensagem_bp
from projeto import projeto_bp
from usuario import usuario_bp
from tarefa import tarefa_bp
from equipe import equipe_bp
from habilidade import habilidade_bp
from feedback import feedback_bp
from problema import problema_bp
import os

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Função para rodar o seed uma única vez
def executar_seed():
    total_usuarios = db.session.query(db.func.count(Usuario.id)).scalar()
    total_projetos = db.session.query(db.func.count(Projeto.id)).scalar()

    if total_usuarios == 0 and total_projetos == 0:
        seed_data()

# Verificar e rodar o seed antes de qualquer requisição
@app.before_request
def verificar_seed():
    executar_seed()

# Rota inicial
@app.route('/')
def index():
    return "Bem-vindo ao app Flask!"

@app.route('/verificar_seed', methods=['GET'])
def verificar_seed_status():
    total_usuarios = db.session.query(db.func.count(Usuario.id)).scalar()
    total_projetos = db.session.query(db.func.count(Projeto.id)).scalar()

    if total_usuarios > 0 and total_projetos > 0:
        return jsonify({
            "usuarios": total_usuarios,
            "projetos": total_projetos,
            "mensagem": "Seed alimentado corretamente!"
        }), 200
    else:
        return jsonify({
            "usuarios": total_usuarios,
            "projetos": total_projetos,
            "mensagem": "Seed não foi executado corretamente."
        }), 200


# Registro dos Blueprints
app.register_blueprint(mensagem_bp, url_prefix='/mensagens')
app.register_blueprint(projeto_bp, url_prefix='/projetos')
app.register_blueprint(usuario_bp, url_prefix='/usuarios')
app.register_blueprint(tarefa_bp, url_prefix='/tarefas')
app.register_blueprint(equipe_bp, url_prefix='/equipes')
app.register_blueprint(habilidade_bp, url_prefix='/habilidades')
app.register_blueprint(feedback_bp, url_prefix='/feedback')
app.register_blueprint(problema_bp, url_prefix='/problemas')

if __name__ == '__main__':
    with app.app_context():
        executar_seed()
    app.run(debug=True, host='0.0.0.0', port=5000)
