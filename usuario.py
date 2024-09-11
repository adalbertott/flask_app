from flask import Blueprint, request, jsonify
from models import db, Usuario
import json

usuario_bp = Blueprint('usuario', __name__)

from flask import Blueprint, request, jsonify
from models import db, Usuario
import json

usuario_bp = Blueprint('usuario', __name__)

# Rota para cadastrar um novo usuário
@usuario_bp.route('/', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    # Normaliza o email para evitar problemas de formatação
    email_normalizado = dados['email'].strip().lower()

    # Verifica se o usuário já existe no banco de dados
    if Usuario.query.filter_by(email=email_normalizado).first():
        return jsonify({"message": "Usuário já existe!"}), 409
    
    # Cria um novo usuário com os dados recebidos
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=email_normalizado,
        habilidades=','.join(dados['habilidades']),
        nivel=dados['nivel'],
        formacao=dados.get('formacao'),
        instituicao=dados.get('instituicao'),
        vinculo=dados.get('vinculo'),
        especialidades=dados.get('especialidades'),
        historico='[]',  # Inicializa o histórico como uma lista vazia
        moedas_trabalho=100,  # Valor inicial de moedas
        pontos=0,  # Inicializa os pontos com zero
        badges=''  # Inicializa sem badges
    )

    # Adiciona o novo usuário ao banco de dados
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

# Rota para listar todos os usuários cadastrados
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

# Rota para obter o perfil de um usuário pelo email
@usuario_bp.route('/perfil_usuario', methods=['GET'])
def obter_perfil_usuario():
    # Normaliza o email recebido para evitar problemas de formatação
    email = request.args.get('email').strip().lower()

    # Tenta encontrar o usuário com o email fornecido
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Usuário não encontrado!"}), 404

    # Retorna os dados do usuário em formato JSON
    return jsonify({
        "nome": usuario.nome,
        "email": usuario.email,
        "nivel": usuario.nivel,
        "habilidades": usuario.habilidades.split(',') if usuario.habilidades else [],
        "historico": json.loads(usuario.historico) if usuario.historico else []
    }), 200
