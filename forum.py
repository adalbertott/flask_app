from flask import Blueprint, request, jsonify
from models import db, Forum, Usuario
from datetime import datetime

forum_bp = Blueprint('forum', __name__)

# Rota para criar um tópico no fórum
@forum_bp.route('/criar_topico', methods=['POST'])
def criar_topico():
    dados = request.json
    titulo = dados.get('titulo')
    criador_id = dados.get('criador_id')
    conteudo = dados.get('conteudo')

    # Verifica se todos os campos obrigatórios foram fornecidos
    if not titulo or not criador_id or not conteudo:
        return jsonify({"message": "Campos obrigatórios faltando"}), 400

    # Cria um novo tópico no fórum
    novo_topico = Forum(
        titulo=titulo,
        criador_id=criador_id,
        conteudo=conteudo,
        data_criacao=datetime.utcnow()
    )

    # Adiciona o tópico ao banco de dados
    db.session.add(novo_topico)
    db.session.commit()

    return jsonify({"message": "Tópico criado com sucesso!"}), 201

# Rota para listar todos os tópicos do fórum
@forum_bp.route('/listar_topicos', methods=['GET'])
def listar_topicos():
    topicos = Forum.query.all()
    resultado = [
        {
            "id": topico.id,
            "titulo": topico.titulo,
            "criador_id": topico.criador_id,
            "conteudo": topico.conteudo,
            "data_criacao": topico.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
        }
        for topico in topicos
    ]
    return jsonify(resultado), 200

# Rota para obter os detalhes de um tópico específico
@forum_bp.route('/topico/<int:topico_id>', methods=['GET'])
def obter_topico(topico_id):
    topico = Forum.query.get(topico_id)
    if not topico:
        return jsonify({"message": "Tópico não encontrado!"}), 404

    resultado = {
        "id": topico.id,
        "titulo": topico.titulo,
        "criador_id": topico.criador_id,
        "conteudo": topico.conteudo,
        "data_criacao": topico.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(resultado), 200
