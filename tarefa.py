from flask import Blueprint, request, jsonify
from models import db, Tarefa

tarefa_bp = Blueprint('tarefa', __name__)

@tarefa_bp.route('/', methods=['POST'])
def criar_tarefa():
    dados = request.json
    nova_tarefa = Tarefa(
        descricao=dados['descricao'],
        complexidade=dados['complexidade'],
        valor=dados['valor']
    )
    db.session.add(nova_tarefa)
    db.session.commit()
    return jsonify({"message": "Tarefa criada com sucesso!"}), 201

@tarefa_bp.route('/listar', methods=['GET'])
def listar_tarefas():
    tarefas = Tarefa.query.all()
    resultado = []
    for tarefa in tarefas:
        resultado.append({
            'id': tarefa.id,
            'descricao': tarefa.descricao,
            'complexidade': tarefa.complexidade,
            'valor': tarefa.valor
        })
    return jsonify(resultado), 200
