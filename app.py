from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados SQLite (ou outro banco configurado no Flask)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'  # Substitua conforme necessário
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

# Criar as tabelas no banco de dados
with app.app_context():
    db.create_all()

# Rota para listar todos os projetos
@app.route('/projetos', methods=['GET'])
def listar_projetos():
    projetos = Projeto.query.all()
    resultado = []
    for projeto in projetos:
        resultado.append({
            'id': projeto.id,
            'nome': projeto.nome,
            'descricao': projeto.descricao,
            'equipe': projeto.equipe,
            'status': projeto.status,
            'comentarios': projeto.comentarios,
            'prazo_revisao': projeto.prazo_revisao,
            'recursos_aprovados': projeto.recursos_aprovados
        })
    return jsonify(resultado), 200

# Rota para criar um novo projeto
@app.route('/projetos', methods=['POST'])
def criar_projeto():
    dados = request.json
    novo_projeto = Projeto(
        nome=dados['nome'],
        descricao=dados['descricao'],
        equipe=dados['equipe'],
        status='Pendente'  # Inicialmente, o status será "Pendente"
    )
    db.session.add(novo_projeto)
    db.session.commit()
    return jsonify({"message": "Projeto criado com sucesso!"}), 201

# Rota para retificar um projeto
@app.route('/retificar_projeto', methods=['POST'])
def retificar_projeto():
    dados = request.json
    projeto = Projeto.query.get(dados['id'])
    if projeto:
        projeto.descricao = dados['descricao']
        db.session.commit()
        return jsonify({"message": "Projeto retificado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para aprovar um projeto
@app.route('/aprovar_projeto', methods=['POST'])
def aprovar_projeto():
    projeto_id = request.json.get('id')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Aprovado"
        db.session.commit()
        return jsonify({"message": "Projeto aprovado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para aprovar um projeto com ressalvas
@app.route('/aprovar_com_ressalvas', methods=['POST'])
def aprovar_com_ressalvas():
    projeto_id = request.json.get('id')
    comentarios = request.json.get('comentarios')
    prazo_revisao = request.json.get('prazo_revisao')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Aprovado com Ressalvas"
        projeto.comentarios = comentarios
        projeto.prazo_revisao = prazo_revisao
        db.session.commit()
        return jsonify({"message": "Projeto aprovado com ressalvas!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para reprovar um projeto
@app.route('/reprovar_projeto', methods=['POST'])
def reprovar_projeto():
    projeto_id = request.json.get('id')
    comentarios = request.json.get('comentarios')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Reprovado"
        projeto.comentarios = comentarios
        db.session.commit()
        return jsonify({"message": "Projeto reprovado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para cadastrar um novo usuário
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({"message": "Usuário já existe!"}), 409
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        habilidades=','.join(dados['habilidades']),
        nivel=dados['nivel'],
        historico='[]'  # Inicializa o histórico como uma lista vazia em formato JSON
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

# Rota para listar todos os usuários
@app.route('/listar_usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for usuario in usuarios:
        resultado.append({
            'nome': usuario.nome,
            'email': usuario.email,
            'habilidades': usuario.habilidades.split(','),
            'nivel': usuario.nivel,
            'historico': usuario.historico
        })
    return jsonify(resultado), 200

# Rota para listar todas as habilidades
@app.route('/listar_habilidades', methods=['GET'])
def listar_habilidades():
    habilidades = Habilidade.query.all()
    resultado = [{'id': habilidade.id, 'nome': habilidade.nome} for habilidade in habilidades]
    return jsonify(resultado), 200

# Rota para obter o perfil de um usuário
@app.route('/perfil_usuario', methods=['GET'])
def perfil_usuario():
    email = request.args.get('email')
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        perfil = {
            'nome': usuario.nome,
            'email': usuario.email,
            'habilidades': usuario.habilidades.split(','),
            'nivel': usuario.nivel,
            'historico': usuario.historico
        }
        return jsonify(perfil), 200
    return jsonify({"message": "Usuário não encontrado!"}), 404

# Rota para salvar habilidades (apenas para fins de exemplo, se precisar adicionar habilidades ao banco)
@app.route('/salvar_habilidade', methods=['POST'])
def salvar_habilidade():
    nome_habilidade = request.json.get('nome')
    if Habilidade.query.filter_by(nome=nome_habilidade).first():
        return jsonify({"message": "Habilidade já existe!"}), 409
    nova_habilidade = Habilidade(nome=nome_habilidade)
    db.session.add(nova_habilidade)
    db.session.commit()
    return jsonify({"message": "Habilidade salva com sucesso!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
