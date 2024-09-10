from flask import Blueprint, request, jsonify
from models import db, Projeto, FaseProjeto

projeto_bp = Blueprint('projeto', __name__)

@projeto_bp.route('/', methods=['POST'])
def criar_projeto():
    dados = request.json
    if not dados.get('nome') or not dados.get('descricao') or not dados.get('recursos_necessarios'):
        return jsonify({"error": "Faltam campos obrigatórios!"}), 400
    try:
        novo_projeto = Projeto(
            nome=dados['nome'],
            descricao=dados['descricao'],
            equipe=dados.get('equipe', ''),
            status="Em avaliação",
            recursos_necessarios=dados['recursos_necessarios']
        )
        db.session.add(novo_projeto)
        db.session.commit()
        return jsonify({"message": "Projeto criado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar o projeto: {str(e)}"}), 500

@projeto_bp.route('/<int:projeto_id>/progresso', methods=['GET'])
def progresso_projeto(projeto_id):
    projeto = Projeto.query.get(projeto_id)
    if not projeto:
        return jsonify({"error": "Projeto não encontrado"}), 404
    progresso_financeiro = projeto.calcular_progresso_financeiro()
    progresso_trabalho = projeto.calcular_progresso_trabalho()
    return jsonify({
        "progresso_financeiro": progresso_financeiro,
        "progresso_trabalho": progresso_trabalho
    }), 200

@projeto_bp.route('/alocar_recursos', methods=['POST'])
def alocar_recursos():
    dados = request.json
    projeto_id = dados['id']
    recursos_totais = dados['recursos_totais']
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        if projeto.nivel_atual == 1:
            recursos_necessarios = projeto.recursos_necessarios * 0.20
        elif projeto.nivel_atual == 2:
            recursos_necessarios = projeto.recursos_necessarios * 0.30
        elif projeto.nivel_atual == 3:
            recursos_necessarios = projeto.recursos_necessarios * 0.50

        if recursos_totais >= recursos_necessarios:
            projeto.recursos_aprovados += recursos_necessarios
            if projeto.recursos_aprovados >= projeto.recursos_necessarios * (projeto.nivel_atual / 3):
                projeto.nivel_atual += 1
            db.session.commit()
            return jsonify({"message": "Recursos alocados e projeto atualizado!"}), 200
        else:
            return jsonify({"message": "Recursos insuficientes para esta alocação!"}), 400
    return jsonify({"message": "Projeto não encontrado!"}), 404
