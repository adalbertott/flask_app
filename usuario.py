from flask import Blueprint, request, jsonify
from models import db, Usuario
import json

usuario_bp = Blueprint('usuario', __name__)

# Rota para cadastrar um novo usuário
@usuario_bp.route('/', methods=['POST'])
def cadastrar_usuario():
    dados = request.json

    # Validar os dados recebidos
    if not dados.get('nome') or not dados.get('email') or not dados.get('nivel'):
        return jsonify({"error": "Campos obrigatórios estão faltando!"}), 400

    email_normalizado = dados['email'].strip().lower()

    # Verifica se o usuário já existe
    if Usuario.query.filter_by(email=email_normalizado).first():
        return jsonify({"message": "Usuário já existe!"}), 409

    # Tentar cadastrar o novo usuário
    try:
        novo_usuario = Usuario(
            nome=dados['nome'],
            email=email_normalizado,
            habilidades=','.join(dados.get('habilidades', [])),
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao cadastrar usuário: {str(e)}"}), 500

# Rota para listar todos os usuários
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

# Rota para obter o perfil de um usuário
@usuario_bp.route('/perfil_usuario', methods=['GET'])
def obter_perfil_usuario():
    email = request.args.get('email').strip().lower()

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Usuário não encontrado!"}), 404

    return jsonify({
        "nome": usuario.nome,
        "email": usuario.email,
        "nivel": usuario.nivel,
        "habilidades": usuario.habilidades.split(',') if usuario.habilidades else [],
        "historico": json.loads(usuario.historico) if usuario.historico else []
    }), 200
