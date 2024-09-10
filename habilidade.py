from flask import Blueprint, request, jsonify
from models import db, Habilidade

habilidade_bp = Blueprint('habilidade', __name__)

@habilidade_bp.route('/', methods=['POST'])
def salvar_habilidade():
    nome_habilidade = request.json.get('nome')
    if Habilidade.query.filter_by(nome=nome_habilidade).first():
        return jsonify({"message": "Habilidade já existe!"}), 409
    nova_habilidade = Habilidade(nome=nome_habilidade)
    db.session.add(nova_habilidade)
    db.session.commit()
    return jsonify({"message": "Habilidade salva com sucesso!"}), 201

@habilidade_bp.route('/listar', methods=['GET'])
def listar_habilidades():
    habilidades = Habilidade.query.all()
    resultado = [{'id': habilidade.id, 'nome': habilidade.nome} for habilidade in habilidades]
    return jsonify(resultado), 200
