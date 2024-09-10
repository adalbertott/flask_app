from flask import Blueprint, request, jsonify
from models import db, Usuario
import json

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({"message": "Usuário já existe!"}), 409
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        habilidades=','.join(dados['habilidades']),
        nivel=dados['nivel'],
        formacao=dados.get('formacao'),
        instituicao=dados.get('instituicao'),
        vinculo=dados.get('vinculo'),
        especialidades=dados.get('especialidades'),
        historico='[]',
        moedas_trabalho=100,
        pontos=0,
        badges=''
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

@usuario_bp.route('/listar', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for usuario in usuarios:
        resultado.append({
            'nome': usuario.nome,
            'email': usuario.email,
            'habilidades': usuario.habilidades.split(',') if usuario.habilidades else [],
            'nivel': usuario.nivel,
            'historico': json.loads(usuario.historico) if usuario.historico else []
        })
    return jsonify(resultado), 200
