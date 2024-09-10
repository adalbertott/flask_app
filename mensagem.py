from flask import Blueprint, request, jsonify
from models import db, Mensagem
from datetime import datetime

mensagem_bp = Blueprint('mensagem', __name__)

@mensagem_bp.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    remetente_id = dados.get('remetente_id')
    destinatario_id = dados.get('destinatario_id')
    conteudo = dados.get('conteudo')

    if not remetente_id or not destinatario_id or not conteudo:
        return jsonify({"message": "Campos obrigatórios faltando"}), 400

    nova_mensagem = Mensagem(
        remetente_id=remetente_id,
        destinatario_id=destinatario_id,
        conteudo=conteudo,
        data_envio=datetime.utcnow()
    )

    db.session.add(nova_mensagem)
    db.session.commit()

    return jsonify({"message": "Mensagem enviada com sucesso!"}), 201

@mensagem_bp.route('/listar_mensagens_enviadas/<int:usuario_id>', methods=['GET'])
def listar_mensagens_enviadas(usuario_id):
    mensagens = Mensagem.query.filter_by(remetente_id=usuario_id).all()
    resultado = [
        {
            "id": mensagem.id,
            "destinatario_id": mensagem.destinatario_id,
            "conteudo": mensagem.conteudo,
            "data_envio": mensagem.data_envio.strftime('%Y-%m-%d %H:%M:%S')
        }
        for mensagem in mensagens
    ]
    return jsonify(resultado), 200

@mensagem_bp.route('/listar_mensagens_recebidas/<int:usuario_id>', methods=['GET'])
def listar_mensagens_recebidas(usuario_id):
    mensagens = Mensagem.query.filter_by(destinatario_id=usuario_id).all()
    resultado = [
        {
            "id": mensagem.id,
            "remetente_id": mensagem.remetente_id,
            "conteudo": mensagem.conteudo,
            "data_envio": mensagem.data_envio.strftime('%Y-%m-%d %H:%M:%S')
        }
        for mensagem in mensagens
    ]
    return jsonify(resultado), 200
