from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from flask_migrate import Migrate
from models import db, Projeto, FaseProjeto, Usuario, Habilidade, Tarefa, Equipe, AvaliacaoEquipe, AtividadeEquipe, Mensagem, Forum, GrandeProblema 
from seed_data import seed_data


app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)  # Certifique-se de incluir esta linha

@app.route('/')
def index():
    return "Bem-vindo ao sistema de gerenciamento de projetos!"


def executar_seed():
    if not hasattr(app, '_seed_executado'):
        seed_data()
        app._seed_executado = True

@app.before_request
def verificar_seed():
    if not hasattr(app, '_seed_executado'):
        executar_seed()



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
    nome = dados.get('nome')
    descricao = dados.get('descricao')
    equipe = dados.get('equipe')
    recursos_necessarios = dados.get('recursos_necessarios')
    grande_problema_id = dados.get('grande_problema_id')
    sugestao_problema = dados.get('sugestao_problema')

    if not nome or not descricao or not equipe or not recursos_necessarios:
        return jsonify({"error": "Todos os campos obrigatórios devem ser preenchidos"}), 400

    # Verifica se o grande_problema_id está vazio e há uma sugestão de problema
    if not grande_problema_id and sugestao_problema:
        novo_problema = GrandeProblema(nome=sugestao_problema, descricao="Sugerido pelo usuário")
        db.session.add(novo_problema)
        db.session.commit()
        grande_problema_id = novo_problema.id  # Agora vincula o novo problema ao projeto

    novo_projeto = Projeto(
        nome=nome,
        descricao=descricao,
        equipe=equipe,
        recursos_necessarios=recursos_necessarios,
        grande_problema_id=grande_problema_id
    )
    db.session.add(novo_projeto)
    db.session.commit()

    return jsonify({"message": "Projeto criado com sucesso!"}), 201

# Rota para alocar recursos em um projeto
@app.route('/alocar_recursos', methods=['POST'])
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

# Rota para alocar recursos por fase de um projeto
@app.route('/alocar_recursos_fase', methods=['POST'])
def alocar_recursos_fase():
    dados = request.json
    projeto_id = dados['projeto_id']
    fase_id = dados['fase_id']
    recursos_totais = dados['recursos_totais']

    projeto = Projeto.query.get(projeto_id)
    fase = FaseProjeto.query.get(fase_id)
    if projeto and fase:
        recursos_necessarios = projeto.recursos_necessarios * (fase.percentual / 100)

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
    
    # Verifica se o e-mail já existe no banco de dados
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({"message": "Usuário já existe!"}), 409
    
    # Criação do novo usuário
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        habilidades=','.join(dados['habilidades']),  # Converte a lista de habilidades para uma string separada por vírgulas
        nivel=dados['nivel'],
        formacao=dados.get('formacao'),  # Usando o método get() para lidar com campos opcionais
        instituicao=dados.get('instituicao'),
        vinculo=dados.get('vinculo'),
        especialidades=dados.get('especialidades'),
        historico='[]'  # Inicializa o histórico como uma lista vazia em formato JSON
    )
    
    # Adiciona o novo usuário ao banco de dados
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

# Rota para salvar habilidades
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

# Rota para listar feedbacks
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

# Rota para registrar feedback
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

# Rota para gerar relatório de auditoria
@app.route('/gerar_relatorio_auditoria', methods=['GET'])
def gerar_relatorio_auditoria():
    auditorias = Feedback.query.all()
    relatorio_conteudo = f"Total de auditorias realizadas: {len(auditorias)}"
    return jsonify({"conteudo": relatorio_conteudo}), 200

# Rota para criar grande questão
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

# Rota para listar os grandes problemas existentes
@app.route('/grandes_problemas', methods=['GET'])
def listar_grandes_problemas():
    grandes_problemas = GrandeProblema.query.all()
    resultado = [{"id": problema.id, "nome": problema.nome, "descricao": problema.descricao} for problema in grandes_problemas]
    return jsonify(resultado), 200

# Rota para enviar mensagem
@app.route('/enviar_mensagem', methods=['POST'])
def enviar_mensagem():
    dados = request.json
    remetente_id = dados.get('remetente_id')
    destinatario_id = dados.get('destinatario_id')
    conteudo = dados.get('conteudo')

    if not remetente_id or not destinatario_id or not conteudo:
        return jsonify({"message": "Campos obrigatórios faltando"}), 400

    nova_mensagem = Mensagem(remetente_id=remetente_id, destinatario_id=destinatario_id, conteudo=conteudo)
    db.session.add(nova_mensagem)
    db.session.commit()

    return jsonify({"message": "Mensagem enviada com sucesso!"}), 201

# Rota para listar projetos por hipótese
@app.route('/projetos_por_hipotese', methods=['GET'])
def projetos_por_hipotese():
    hipotese_id = request.args.get('hipotese_id')
    projetos = Projeto.query.filter_by(hipotese_id=hipotese_id).all()
    resultado = [{'id': p.id, 'nome': p.nome, 'descricao': p.descricao} for p in projetos]
    return jsonify(resultado), 200

# Rota para contribuir em um projeto
@app.route('/projetos/<int:projeto_id>/contribuir', methods=['POST'])
def contribuir_projeto(projeto_id):
    dados = request.json
    tipo_contribuicao = dados.get('tipo')
    valor = dados.get('valor')

    projeto = Projeto.query.get(projeto_id)
    
    if not projeto:
        return jsonify({"error": "Projeto não encontrado"}), 404
    
    if tipo_contribuicao == 'financeira':
        projeto.contribuicao_financeira += valor
    elif tipo_contribuicao == 'trabalho':
        projeto.contribuicao_trabalho += valor
    else:
        return jsonify({"error": "Tipo de contribuição inválido"}), 400

    db.session.commit()
    
    return jsonify({"message": "Contribuição adicionada com sucesso!"}), 200

# Rota para consultar o progresso de um projeto
@app.route('/projetos/<int:projeto_id>/progresso', methods=['GET'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
   
