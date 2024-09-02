from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'
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

# Rota para apoiar um projeto
@app.route('/apoiar_projeto', methods=['POST'])
def apoiar_projeto():
    projeto_id = request.json.get('id')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.recursos_aprovados += 10  # Exemplo: Incrementar 10% de apoio
        db.session.commit()
        return jsonify({"message": "Apoio registrado com sucesso!"}), 200
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
