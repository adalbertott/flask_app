from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db
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
migrate = Migrate(app, db)  # Certifique-se de incluir esta linha

# Função para executar o seed
def executar_seed():
    if not hasattr(app, '_seed_executado'):
        seed_data()
        app._seed_executado = True

# Verificar e rodar o seed antes da primeira requisição
@app.before_request
def verificar_seed():
    executar_seed()

# Rota inicial
@app.route('/')
def index():
    return "Bem-vindo ao app Flask!"

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
