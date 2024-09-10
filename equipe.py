from flask import Blueprint, request, jsonify
from models import db, Equipe, Usuario

equipe_bp = Blueprint('equipe', __name__)

@equipe_bp.route('/', methods=['POST'])
def criar_equipe():
    dados = request.json
    nova_equipe = Equipe(nome=dados['nome'])
    db.session.add(nova_equipe)
    db.session.commit()
    return jsonify({"message": "Equipe criada com sucesso!"}), 201

@equipe_bp.route('/listar', methods=['GET'])
def listar_equipes():
    equipes = Equipe.query.all()
    resultado = [{'id': equipe.id, 'nome': equipe.nome} for equipe in equipes]
    return jsonify(resultado), 200

@equipe_bp.route('/atribuir_membro', methods=['POST'])
def atribuir_membro_equipe():
    dados = request.json
    equipe = Equipe.query.get(dados['equipe_id'])
    usuario = Usuario.query.get(dados['usuario_id'])
    if equipe and usuario:
        equipe.membros.append(usuario)
        db.session.commit()
        return jsonify({"message": "Membro atribuído à equipe com sucesso!"}), 200
    return jsonify({"message": "Equipe ou usuário não encontrados!"}), 404
