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
migrate = Migrate(app, db)

# Verificar se o seed já foi executado
seed_executado = False

# Função para rodar o seed uma única vez
def executar_seed():
    global seed_executado
    if not seed_executado:
        seed_data()  # Executa o seed apenas se ainda não tiver sido rodado
        seed_executado = True

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
    # Para garantir que o seed é executado ao iniciar o app
    with app.app_context():
        executar_seed()

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
