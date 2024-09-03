from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados (aqui você pode trocar para um banco de dados diferente de SQLite se desejar)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados2.db'  # Substitua conforme necessário
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Projeto
class Projeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    equipe = db.Column(db.String(200))
    status = db.Column(db.String(50), nullable=False)
    comentarios = db.Column(db.Text)
    prazo_revisao = db.Column(db.String(50))
    recursos_aprovados = db.Column(db.Integer, default=0)

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

# Modelo de Grande Área
class GrandeArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Modelo de Hipótese
class Hipotese(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grande_area_id = db.Column(db.Integer, db.ForeignKey('grande_area.id'))
    descricao = db.Column(db.Text, nullable=False)

# Modelo de Questão
class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grande_area_id = db.Column(db.Integer, db.ForeignKey('grande_area.id'))
    descricao = db.Column(db.Text, nullable=False)

# Modelo de Problema
class Problema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grande_area_id = db.Column(db.Integer, db.ForeignKey('grande_area.id'))
    descricao = db.Column(db.Text, nullable=False)
    impacto = db.Column(db.Text, nullable=True)

# Modelo de Possibilidade de Solução
class PossibilidadeSolucao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problema_id = db.Column(db.Integer, db.ForeignKey('problema.id'))
    descricao = db.Column(db.Text, nullable=False)

# Função para popular o banco de dados com as grandes áreas e suas informações
def popular_banco_de_dados():
    grandes_areas_dados = {
        "Energia e Sustentabilidade": {
            "hipoteses": [
                "A redução das emissões de CO2 em processos industriais pode mitigar significativamente os efeitos das mudanças climáticas.",
                "O desenvolvimento e a adoção de energias renováveis são cruciais para reduzir a dependência de combustíveis fósseis e limitar o aquecimento global.",
                "A transição para fontes de energia renováveis, como solar, eólica e hidrelétrica, pode reduzir significativamente a pegada de carbono e a dependência de combustíveis fósseis."
            ],
            "questoes": [
                "Como reduzir as emissões de CO2 em processos industriais sem comprometer a produtividade?",
                "Quais tecnologias de energia renovável oferecem a melhor combinação de escalabilidade e eficiência?",
                "Como lidar com o armazenamento de energia, intermitência das fontes renováveis e custos iniciais de instalação?"
            ],
            "problemas": {
                "Redução de Emissões de CO2 em Processos Industriais": {
                    "descricao": "Desenvolver soluções para reduzir as emissões de CO2 em processos industriais, focando em tecnologias e processos que possam ser implementados em fábricas de médio e grande porte.",
                    "impacto": "Redução significativa das emissões de gases de efeito estufa, contribuindo para o combate às mudanças climáticas.",
                    "possibilidades_de_solucao": [
                        {
                            "descricao": "Identificar e analisar tecnologias existentes que já são usadas para a redução de emissões de CO2."
                        },
                        {
                            "descricao": "Identificar os principais padrões de emissão de CO2 em diferentes tipos de processos industriais."
                        },
                        {
                            "descricao": "Criar propostas de soluções inovadoras que possam ser implementadas para reduzir emissões em processos industriais."
                        }
                    ]
                }
            }
        },
        "Agricultura e Alimentação": {
            "hipoteses": [
                "O uso de tecnologias avançadas, como sensores e drones, pode otimizar o uso de recursos e aumentar a produtividade, reduzindo desperdícios e melhorando a sustentabilidade.",
                "A biotecnologia pode desenvolver cultivares mais resistentes a pragas e mudanças climáticas, além de melhorar a qualidade nutricional dos alimentos.",
                "A agricultura vertical e a produção de alimentos em ambientes urbanos podem reduzir a pegada de carbono associada ao transporte e promover a segurança alimentar local."
            ],
            "questoes": [
                "Como superar os custos iniciais elevados e integrar as novas tecnologias agrícolas com as práticas existentes?",
                "Quais são os impactos ecológicos e éticos da biotecnologia no cultivo de plantas?",
                "Como garantir a viabilidade econômica e a aceitação do mercado para a agricultura vertical?"
            ],
            "problemas": {
                "Custo e Complexidade das Tecnologias de Agricultura de Precisão": {
                    "descricao": "Alta barreira de entrada devido aos custos e complexidade técnica das tecnologias, que pode limitar a adoção por pequenos produtores."
                },
                "Segurança e Ética na Biotecnologia": {
                    "descricao": "Questões sobre segurança alimentar e ética podem gerar resistência à aceitação pública e enfrentar desafios regulatórios."
                },
                "Viabilidade Econômica da Agricultura Vertical": {
                    "descricao": "Os altos custos iniciais e a necessidade de alta eficiência energética podem dificultar a viabilidade econômica e a adoção em larga escala."
                }
            }
        }
    }

    for area_nome, conteudo in grandes_areas_dados.items():
        grande_area = GrandeArea(nome=area_nome)
        db.session.add(grande_area)
        db.session.commit()

        for hipotese_desc in conteudo["hipoteses"]:
            hipotese = Hipotese(grande_area_id=grande_area.id, descricao=hipotese_desc)
            db.session.add(hipotese)

        for questao_desc in conteudo["questoes"]:
            questao = Questao(grande_area_id=grande_area.id, descricao=questao_desc)
            db.session.add(questao)

        for problema_nome, problema_conteudo in conteudo["problemas"].items():
            problema = Problema(
                grande_area_id=grande_area.id,
                descricao=problema_conteudo["descricao"],
                impacto=problema_conteudo.get("impacto", "")
            )
            db.session.add(problema)
            db.session.commit()

            for solucao in problema_conteudo.get("possibilidades_de_solucao", []):
                possivel_solucao = PossibilidadeSolucao(
                    problema_id=problema.id,
                    descricao=solucao["descricao"]
                )
                db.session.add(possivel_solucao)

    db.session.commit()

# Criar as tabelas no banco de dados e popular
with app.app_context():
    db.create_all()
    popular_banco_de_dados()

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
            'recursos_aprovados': projeto.recursos_aprovados
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
        status='Pendente'  # Inicialmente, o status será "Pendente"
    )
    db.session.add(novo_projeto)
    db.session.commit()
    return jsonify({"message": "Projeto criado com sucesso!"}), 201

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
    projeto_id = request.json.get('id')
    comentarios = request.json.get('comentarios')
    prazo_revisao = request.json.get('prazo_revisao')
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
    projeto_id = request.json.get('id')
    comentarios = request.json.get('comentarios')
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
            'habilidades': usuario.habilidades.split(','),
            'nivel': usuario.nivel,
            'historico': usuario.historico
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
            'habilidades': usuario.habilidades.split(','),
            'nivel': usuario.nivel,
            'historico': usuario.historico
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
        historico = json.loads(usuario.historico)  # Converte a string JSON de volta para uma lista
        return jsonify(historico), 200
    return jsonify({"message": "Usuário não encontrado!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
