from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Certifique-se de incluir esta linha

class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    equipe = db.Column(db.String(200))
    status = db.Column(db.String(50), nullable=False)
    comentarios = db.Column(db.Text)
    prazo_revisao = db.Column(db.String(50))
    recursos_aprovados = db.Column(db.Integer, default=0)
    nivel_atual = db.Column(db.Integer, default=1)  # Nível do projeto (1, 2, 3)
    recursos_necessarios = db.Column(db.Integer, nullable=False)  # Total de recursos necessários
    recursos_manutencao = db.Column(db.Integer, default=0)  # Recursos para manutenção

    # Novos campos:
    contribuicao_financeira = db.Column(db.Float, default=0)  # Contribuição financeira
    contribuicao_trabalho = db.Column(db.Float, default=0)  # Contribuição de trabalho

    fases = db.relationship('FaseProjeto', backref='projeto', lazy=True)

@app.route('/')
def index():
    return "Bem-vindo ao sistema de gerenciamento de projetos!"

# Modelo de Fase do Projeto
class FaseProjeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    percentual = db.Column(db.Float, nullable=False)  # Percentual de recursos para a fase
    completada = db.Column(db.Boolean, default=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    habilidades = db.Column(db.Text)  # Armazenado como uma string separada por vírgulas
    nivel = db.Column(db.String(50), nullable=False)
    historico = db.Column(db.Text)  # Armazenado como uma string JSON

# Modelo de Habilidade
class Habilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    complexidade = db.Column(db.Integer, nullable=False)  # Nível de complexidade
    valor = db.Column(db.Integer, nullable=False)  # Valor da tarefa baseado na complexidade

# Modelo de Equipe
class Equipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    membros = db.relationship('Usuario', secondary='equipe_membros', backref='equipes')

# Tabela associativa para usuários em equipes
equipe_membros = db.Table('equipe_membros',
    db.Column('equipe_id', db.Integer, db.ForeignKey('equipe.id'), primary_key=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
)

# Modelo de Avaliação da Equipe
class AvaliacaoEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    avaliador = db.Column(db.String(100), nullable=False)  # Nome do avaliador
    data_avaliacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nota = db.Column(db.Float, nullable=False)  # Nota de 0 a 10
    comentarios = db.Column(db.Text)

    equipe = db.relationship('Equipe', backref=db.backref('avaliacoes', lazy=True))
    projeto = db.relationship('Projeto', backref=db.backref('avaliacoes', lazy=True))

# Modelo de Atividade da Equipe
class AtividadeEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipe.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_atividade = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    equipe = db.relationship('Equipe', backref=db.backref('atividades', lazy=True))

# Rota para listar todos os projetos
@app.route('/projetos', methods=['GET'])
def listar_projetos():
    projetos = Projeto.query.all()
    resultado = []
    for projeto in projetos:
        resultado.append({
            'id': projeto.id,
            'nome': projeto.nome,
            'descricao': projeto.descricao,
            'equipe': projeto.equipe,
            'status': projeto.status,
            'comentarios': projeto.comentarios,
            'prazo_revisao': projeto.prazo_revisao,
            'recursos_aprovados': projeto.recursos_aprovados,
            'nivel_atual': projeto.nivel_atual,
            'recursos_necessarios': projeto.recursos_necessarios
        })
    return jsonify(resultado), 200

# Rota para criar um novo projeto
@app.route('/projetos', methods=['POST'])
def criar_projeto():
    dados = request.json
    novo_projeto = Projeto(
        nome=dados['nome'],
        descricao=dados['descricao'],
        equipe=dados['equipe'],
        status='Pendente',  # Inicialmente, o status será "Pendente"
        recursos_necessarios=dados['recursos_necessarios']  # Recursos totais necessários para o projeto
    )
    db.session.add(novo_projeto)
    db.session.commit()
    return jsonify({"message": "Projeto criado com sucesso!"}), 201

# Rota para alocar recursos em um projeto com base no nível
@app.route('/alocar_recursos', methods=['POST'])
def alocar_recursos():
    dados = request.json
    projeto_id = dados['id']
    recursos_totais = dados['recursos_totais']  # Recurso total disponível para o ciclo

    projeto = Projeto.query.get(projeto_id)
    if projeto:
        # Definir porcentagens de alocação por nível
        if projeto.nivel_atual == 1:
            recursos_necessarios = projeto.recursos_necessarios * 0.20  # 20% para Nível 1
        elif projeto.nivel_atual == 2:
            recursos_necessarios = projeto.recursos_necessarios * 0.30  # 30% para Nível 2
        elif projeto.nivel_atual == 3:
            recursos_necessarios = projeto.recursos_necessarios * 0.50  # 50% para Nível 3

        # Verificar se os recursos disponíveis são suficientes
        if recursos_totais >= recursos_necessarios:
            projeto.recursos_aprovados += recursos_necessarios

            # Progredir de nível conforme frações do necessário para cada nível
            if projeto.recursos_aprovados >= projeto.recursos_necessarios * (projeto.nivel_atual / 3):
                projeto.nivel_atual += 1  # Avança para o próximo nível

            db.session.commit()
            return jsonify({"message": "Recursos alocados e projeto atualizado!"}), 200
        else:
            return jsonify({"message": "Recursos insuficientes para esta alocação!"}), 400
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para alocar recursos por fase de um projeto
@app.route('/alocar_recursos_fase', methods=['POST'])
def alocar_recursos_fase():
    dados = request.json
    projeto_id = dados['projeto_id']
    fase_id = dados['fase_id']
    recursos_totais = dados['recursos_totais']  # Recurso total disponível para a fase

    projeto = Projeto.query.get(projeto_id)
    fase = FaseProjeto.query.get(fase_id)
    if projeto and fase:
        recursos_necessarios = projeto.recursos_necessarios * (fase.percentual / 100)

        # Verificar se os recursos disponíveis são suficientes
        if recursos_totais >= recursos_necessarios and not fase.completada:
            fase.completada = True
            projeto.recursos_aprovados += recursos_necessarios
            db.session.commit()
            return jsonify({"message": "Recursos alocados para a fase com sucesso!"}), 200
        else:
            return jsonify({"message": "Recursos insuficientes ou fase já completada!"}), 400
    return jsonify({"message": "Projeto ou fase não encontrados!"}), 404

# Rota para relatar o progresso de um projeto
@app.route('/relatorio_progresso/<int:projeto_id>', methods=['GET'])
def relatorio_progresso(projeto_id):
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        relatorio = {
            "nome_projeto": projeto.nome,
            "nivel_atual": projeto.nivel_atual,
            "recursos_aprovados": projeto.recursos_aprovados,
            "recursos_necessarios": projeto.recursos_necessarios,
            "progresso": f"{(projeto.recursos_aprovados / projeto.recursos_necessarios) * 100:.2f}%"
        }
        return jsonify(relatorio), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para retificar um projeto
@app.route('/retificar_projeto', methods=['POST'])
def retificar_projeto():
    dados = request.json
    projeto = Projeto.query.get(dados['id'])
    if projeto:
        projeto.descricao = dados['descricao']
        db.session.commit()
        return jsonify({"message": "Projeto retificado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para aprovar um projeto
@app.route('/aprovar_projeto', methods=['POST'])
def aprovar_projeto():
    projeto_id = request.json.get('id')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Aprovado"
        db.session.commit()
        return jsonify({"message": "Projeto aprovado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para aprovar um projeto com ressalvas
@app.route('/aprovar_com_ressalvas', methods=['POST'])
def aprovar_com_ressalvas():
    dados = request.json
    projeto_id = dados.get('id')
    comentarios = dados.get('comentarios')
    prazo_revisao = dados.get('prazo_revisao')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Aprovado com Ressalvas"
        projeto.comentarios = comentarios
        projeto.prazo_revisao = prazo_revisao
        db.session.commit()
        return jsonify({"message": "Projeto aprovado com ressalvas!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para reprovar um projeto
@app.route('/reprovar_projeto', methods=['POST'])
def reprovar_projeto():
    dados = request.json
    projeto_id = dados.get('id')
    comentarios = dados.get('comentarios')
    projeto = Projeto.query.get(projeto_id)
    if projeto:
        projeto.status = "Reprovado"
        projeto.comentarios = comentarios
        db.session.commit()
        return jsonify({"message": "Projeto reprovado com sucesso!"}), 200
    return jsonify({"message": "Projeto não encontrado!"}), 404

# Rota para cadastrar um novo usuário
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({"message": "Usuário já existe!"}), 409
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        habilidades=','.join(dados['habilidades']),
        nivel=dados['nivel'],
        historico='[]'  # Inicializa o histórico como uma lista vazia em formato JSON
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

# Rota para listar todos os usuários
@app.route('/listar_usuarios', methods=['GET'])
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

# Rota para listar todas as habilidades
@app.route('/listar_habilidades', methods=['GET'])
def listar_habilidades():
    habilidades = Habilidade.query.all()
    resultado = [{'id': habilidade.id, 'nome': habilidade.nome} for habilidade in habilidades]
    return jsonify(resultado), 200

# Rota para obter o perfil de um usuário
@app.route('/perfil_usuario', methods=['GET'])
def perfil_usuario():
    email = request.args.get('email')
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        perfil = {
            'nome': usuario.nome,
            'email': usuario.email,
            'habilidades': usuario.habilidades.split(',') if usuario.habilidades else [],
            'nivel': usuario.nivel,
            'historico': json.loads(usuario.historico) if usuario.historico else []
        }
        return jsonify(perfil), 200
    return jsonify({"message": "Usuário não encontrado!"}), 404

# Rota para salvar habilidades (apenas para fins de exemplo, se precisar adicionar habilidades ao banco)
@app.route('/salvar_habilidade', methods=['POST'])
def salvar_habilidade():
    nome_habilidade = request.json.get('nome')
    if Habilidade.query.filter_by(nome=nome_habilidade).first():
        return jsonify({"message": "Habilidade já existe!"}), 409
    nova_habilidade = Habilidade(nome=nome_habilidade)
    db.session.add(nova_habilidade)
    db.session.commit()
    return jsonify({"message": "Habilidade salva com sucesso!"}), 201

# Rota para visualizar o histórico de tarefas do usuário
@app.route('/historico_tarefas', methods=['GET'])
def historico_tarefas():
    email = request.args.get('email')
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        historico = json.loads(usuario.historico) if usuario.historico else []
        return jsonify(historico), 200
    return jsonify({"message": "Usuário não encontrado!"}), 404

# Rota para listar todas as tarefas
@app.route('/listar_tarefas', methods=['GET'])
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

# Rota para criar uma nova tarefa
@app.route('/criar_tarefa', methods=['POST'])
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

# Rota para atualizar uma tarefa
@app.route('/atualizar_tarefa', methods=['PUT'])
def atualizar_tarefa():
    dados = request.json
    tarefa = Tarefa.query.get(dados['id'])
    if tarefa:
        tarefa.descricao = dados['descricao']
        tarefa.complexidade = dados['complexidade']
        tarefa.valor = dados['valor']
        db.session.commit()
        return jsonify({"message": "Tarefa atualizada com sucesso!"}), 200
    return jsonify({"message": "Tarefa não encontrada!"}), 404

# Rota para consultar fases de um projeto
@app.route('/consultar_fases_projeto/<int:projeto_id>', methods=['GET'])
def consultar_fases_projeto(projeto_id):
    fases = FaseProjeto.query.filter_by(projeto_id=projeto_id).all()
    resultado = []
    for fase in fases:
        resultado.append({
            'id': fase.id,
            'descricao': fase.descricao,
            'percentual': fase.percentual,
            'completada': fase.completada
        })
    return jsonify(resultado), 200

# Rota para atualizar uma fase de um projeto
@app.route('/atualizar_fase_projeto/<int:projeto_id>', methods=['PUT'])
def atualizar_fase_projeto(projeto_id):
    dados = request.json
    fase = FaseProjeto.query.get(dados['id'])
    if fase and fase.projeto_id == projeto_id:
        fase.descricao = dados['descricao']
        fase.percentual = dados['percentual']
        fase.completada = dados['completada']
        db.session.commit()
        return jsonify({"message": "Fase atualizada com sucesso!"}), 200
    return jsonify({"message": "Fase não encontrada!"}), 404

# Rota para listar fases de um projeto
@app.route('/listar_fases_projeto', methods=['GET'])
def listar_fases_projeto():
    fases = FaseProjeto.query.all()
    resultado = []
    for fase in fases:
        resultado.append({
            'id': fase.id,
            'descricao': fase.descricao,
            'percentual': fase.percentual,
            'projeto_id': fase.projeto_id,
            'completada': fase.completada
        })
    return jsonify(resultado), 200

# Rota para listar projetos com fases
@app.route('/listar_projetos_fases', methods=['GET'])
def listar_projetos_fases():
    projetos = Projeto.query.all()
    resultado = []
    for projeto in projetos:
        fases = FaseProjeto.query.filter_by(projeto_id=projeto.id).all()
        fases_info = [{'descricao': fase.descricao, 'percentual': fase.percentual, 'completada': fase.completada} for fase in fases]
        resultado.append({
            'id': projeto.id,
            'nome': projeto.nome,
            'fases': fases_info
        })
    return jsonify(resultado), 200

# --- Novas rotas para equipes e avaliações de equipes ---
# Rota para criar uma equipe
@app.route('/criar_equipe', methods=['POST'])
def criar_equipe():
    dados = request.json
    nova_equipe = Equipe(nome=dados['nome'])
    db.session.add(nova_equipe)
    db.session.commit()
    return jsonify({"message": "Equipe criada com sucesso!"}), 201

# Rota para listar todas as equipes
@app.route('/listar_equipes', methods=['GET'])
def listar_equipes():
    equipes = Equipe.query.all()
    resultado = [{'id': equipe.id, 'nome': equipe.nome} for equipe in equipes]
    return jsonify(resultado), 200

# Rota para atribuir membros a uma equipe
@app.route('/atribuir_membro_equipe', methods=['POST'])
def atribuir_membro_equipe():
    dados = request.json
    equipe = Equipe.query.get(dados['equipe_id'])
    usuario = Usuario.query.get(dados['usuario_id'])
    if equipe and usuario:
        equipe.membros.append(usuario)
        db.session.commit()
        return jsonify({"message": "Membro atribuído à equipe com sucesso!"}), 200
    return jsonify({"message": "Equipe ou usuário não encontrados!"}), 404

# Rota para listar membros de uma equipe
@app.route('/listar_membros_equipe/<int:equipe_id>', methods=['GET'])
def listar_membros_equipe(equipe_id):
    equipe = Equipe.query.get(equipe_id)
    if equipe:
        membros = [{'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email} for usuario in equipe.membros]
        return jsonify(membros), 200
    return jsonify({"message": "Equipe não encontrada!"}), 404

# Rota para registrar uma avaliação da equipe
@app.route('/avaliar_equipe', methods=['POST'])
def avaliar_equipe():
    dados = request.json
    avaliacao = AvaliacaoEquipe(
        equipe_id=dados['equipe_id'],
        projeto_id=dados['projeto_id'],
        avaliador=dados['avaliador'],
        nota=dados['nota'],
        comentarios=dados.get('comentarios', '')
    )
    db.session.add(avaliacao)
    db.session.commit()
    return jsonify({"message": "Avaliação registrada com sucesso!"}), 201

# Rota para consultar avaliações de uma equipe
@app.route('/consultar_avaliacoes_equipe/<int:equipe_id>', methods=['GET'])
def consultar_avaliacoes_equipe(equipe_id):
    avaliacoes = AvaliacaoEquipe.query.filter_by(equipe_id=equipe_id).all()
    resultado = []
    for avaliacao in avaliacoes:
        resultado.append({
            'projeto_id': avaliacao.projeto_id,
            'avaliador': avaliacao.avaliador,
            'data_avaliacao': avaliacao.data_avaliacao.strftime('%Y-%m-%d'),
            'nota': avaliacao.nota,
            'comentarios': avaliacao.comentarios
        })
    return jsonify(resultado), 200

# Rota para registrar uma atividade de equipe
@app.route('/registrar_atividade_equipe', methods=['POST'])
def registrar_atividade_equipe():
    dados = request.json
    atividade = AtividadeEquipe(
        equipe_id=dados['equipe_id'],
        descricao=dados['descricao']
    )
    db.session.add(atividade)
    db.session.commit()
    return jsonify({"message": "Atividade registrada com sucesso!"}), 201

# Rota para consultar atividades de uma equipe
@app.route('/consultar_atividades_equipe/<int:equipe_id>', methods=['GET'])
def consultar_atividades_equipe(equipe_id):
    atividades = AtividadeEquipe.query.filter_by(equipe_id=equipe_id).all()
    resultado = []
    for atividade in atividades:
        resultado.append({
            'descricao': atividade.descricao,
            'data_atividade': atividade.data_atividade.strftime('%Y-%m-%d')
        })
    return jsonify(resultado), 200
# Rota para distribuir dividendos
@app.route('/distribuir_dividendos', methods=['POST'])
def distribuir_dividendos():
    dados = request.json
    projeto_id = dados['projeto_id']
    projeto = Projeto.query.get(projeto_id)

    if projeto:
        total_contribuicao = projeto.contribuicao_financeira + projeto.contribuicao_trabalho
        if total_contribuicao > 0:
            dividendos_financeiros = (projeto.contribuicao_financeira / total_contribuicao) * 100
            dividendos_trabalho = (projeto.contribuicao_trabalho / total_contribuicao) * 100
            return jsonify({
                "dividendos_financeiros": f"{dividendos_financeiros:.2f}%",
                "dividendos_trabalho": f"{dividendos_trabalho:.2f}%"
            }), 200
        else:
            return jsonify({"message": "Nenhuma contribuição foi feita."}), 400
    return jsonify({"message": "Projeto não encontrado!"}), 404
# Rota para calcular a média ponderada de um projeto
@app.route('/calcular_media_ponderada', methods=['POST'])
def calcular_media_ponderada():
    dados = request.json
    projeto_id = dados['projeto_id']
    avaliacoes = AvaliacaoEquipe.query.filter_by(projeto_id=projeto_id).all()

    if avaliacoes:
        confiabilidade_total = sum([avaliacao.confiabilidade for avaliacao in avaliacoes])
        impacto_total = sum([avaliacao.impacto for avaliacao in avaliacoes])
        relevancia_total = sum([avaliacao.relevancia for avaliacao in avaliacoes])
        total_avaliacoes = len(avaliacoes)

        media_ponderada = (confiabilidade_total + impacto_total + relevancia_total) / (3 * total_avaliacoes)
        return jsonify({"media_ponderada": f"{media_ponderada:.2f}"}), 200
    return jsonify({"message": "Nenhuma avaliação encontrada!"}), 404

@app.route('/listar_feedbacks', methods=['GET'])
def listar_feedbacks():
    feedbacks = Feedback.query.all()
    resultado = [{
        "projeto_nome": feedback.projeto.nome,
        "auditor": feedback.auditor,
        "conteudo": feedback.conteudo,
        "data": feedback.data_avaliacao.strftime("%Y-%m-%d")
    } for feedback in feedbacks]
    return jsonify(resultado), 200

@app.route('/registrar_feedback', methods=['POST'])
def registrar_feedback():
    dados = request.json
    email = dados.get('email')
    projeto_id = dados.get('projeto_id')
    conteudo = dados.get('feedback')

    if not email or not projeto_id or not conteudo:
        return jsonify({"message": "Dados incompletos"}), 400

    feedback = Feedback(
        projeto_id=projeto_id,
        auditor=email,
        conteudo=conteudo,
        data_avaliacao=datetime.utcnow()
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Feedback registrado com sucesso!"}), 200

@app.route('/gerar_relatorio_auditoria', methods=['GET'])
def gerar_relatorio_auditoria():

    # Esta função pode ser expandida para gerar relatórios mais complexos
    auditorias = Feedback.query.all()
    relatorio_conteudo = f"Total de auditorias realizadas: {len(auditorias)}"
    return jsonify({"conteudo": relatorio_conteudo}), 200

@app.route('/criar_grande_questao', methods=['POST'])
def criar_grande_questao():
    dados = request.json
    nome = dados.get('nome')
    descricao = dados.get('descricao')

    if not nome or not descricao:
        return jsonify({"message": "Nome e descrição são obrigatórios"}), 400

    nova_questao = GrandeQuestao(nome=nome, descricao=descricao)
    db.session.add(nova_questao)
    db.session.commit()

    return jsonify({"message": "Grande questão criada com sucesso!"}), 201

@app.route('/grandes_problemas', methods=['GET'])
def listar_grandes_problemas():
    problemas = GrandeProblema.query.all()
    resultado = [{'id': p.id, 'nome': p.nome} for p in problemas]
    return jsonify(resultado), 200


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
