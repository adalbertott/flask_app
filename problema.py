from flask import Blueprint, request, jsonify
from models import db, GrandeProblema

problema_bp = Blueprint('problema', __name__)

@problema_bp.route('/', methods=['GET'])
def listar_grandes_problemas():
    grandes_problemas = GrandeProblema.query.all()
    resultado = [{"id": problema.id, "nome": problema.nome, "descricao": problema.descricao} for problema in grandes_problemas]
    return jsonify(resultado), 200

@problema_bp.route('/criar', methods=['POST'])
def criar_grande_questao():
    dados = request.json
    nome = dados.get('nome')
    descricao = dados.get('descricao')
    if not nome or not descricao:
        return jsonify({"message": "Nome e descrição são obrigatórios"}), 400
    nova_questao = GrandeProblema(nome=nome, descricao=descricao)
    db.session.add(nova_questao)
    db.session.commit()
    return jsonify({"message": "Grande questão criada com sucesso!"}), 201
