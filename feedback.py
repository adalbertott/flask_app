from flask import Blueprint, request, jsonify
from models import db, Feedback
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/', methods=['POST'])
def registrar_feedback():
    dados = request.json
    feedback = Feedback(
        projeto_id=dados.get('projeto_id'),
        auditor=dados.get('email'),
        conteudo=dados.get('feedback'),
        data_avaliacao=datetime.utcnow()
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "Feedback registrado com sucesso!"}), 200

@feedback_bp.route('/listar', methods=['GET'])
def listar_feedbacks():
    feedbacks = Feedback.query.all()
    resultado = [{
        "projeto_nome": feedback.projeto.nome,
        "auditor": feedback.auditor,
        "conteudo": feedback.conteudo,
        "data": feedback.data_avaliacao.strftime("%Y-%m-%d")
    } for feedback in feedbacks]
    return jsonify(resultado), 200
