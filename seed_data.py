from app import db
from models import (
    GrandeProblema, Projeto, FaseProjeto, Usuario, Habilidade, Tarefa, Equipe, 
    AvaliacaoEquipe, AtividadeEquipe, Mensagem, Forum, GrandeArea, Hipotese, Questao
)
from datetime import datetime

def seed_data():
    # Exemplo de Grande Problema
    problema1 = GrandeProblema(nome="Problema Climático", descricao="Aquecimento global e mudanças climáticas.")
    problema2 = GrandeProblema(nome="Desigualdade Social", descricao="Desigualdade de renda e acesso a recursos.")
    db.session.add_all([problema1, problema2])

    # Exemplo de Grande Área
    area1 = GrandeArea(nome="Tecnologia", descricao="Inovações e avanços tecnológicos.")
    area2 = GrandeArea(nome="Saúde", descricao="Questões relacionadas à saúde pública.")
    db.session.add_all([area1, area2])

    # Exemplo de Hipótese
    hipotese1 = Hipotese(nome="Fusão Nuclear", descricao="Fusão nuclear pode ser a solução para a crise energética.")
    hipotese2 = Hipotese(nome="Imunoterapia", descricao="Imunoterapia pode curar cânceres agressivos.")
    db.session.add_all([hipotese1, hipotese2])

    # Exemplo de Questão
    questao1 = Questao(nome="Energia Limpa", descricao="Como a fusão nuclear pode ser usada para energia limpa?")
    questao2 = Questao(nome="Tratamento de Câncer", descricao="Imunoterapia é eficaz para todos os tipos de câncer?")
    db.session.add_all([questao1, questao2])

    # Exemplo de Projetos
    projeto1 = Projeto(
        nome="Projeto Energia Sustentável", descricao="Projeto para desenvolver tecnologias de fusão nuclear.",
        equipe="Equipe Fusão", status="Em progresso", recursos_necessarios=10000, grande_problema_id=problema1.id,
        sugestao_problema="Falta de investimentos em energia limpa.", contribuicao_financeira=5000, contribuicao_trabalho=100
    )
    projeto2 = Projeto(
        nome="Projeto Saúde Global", descricao="Desenvolvimento de imunoterapia para câncer.",
        equipe="Equipe Saúde", status="Em avaliação", recursos_necessarios=15000, grande_problema_id=problema2.id,
        sugestao_problema="Falta de tratamento para cânceres agressivos.", contribuicao_financeira=7000, contribuicao_trabalho=200
    )
    db.session.add_all([projeto1, projeto2])

    # Exemplo de Fases do Projeto
    fase1 = FaseProjeto(descricao="Pesquisa Inicial", percentual=20.0, projeto_id=projeto1.id)
    fase2 = FaseProjeto(descricao="Desenvolvimento de Protótipo", percentual=50.0, projeto_id=projeto1.id)
    fase3 = FaseProjeto(descricao="Pesquisa Clínica", percentual=30.0, projeto_id=projeto2.id)
    db.session.add_all([fase1, fase2, fase3])

    # Exemplo de Usuários
    usuario1 = Usuario(nome="João Silva", email="joao@example.com", habilidades="Física, Programação", nivel="Especialista")
    usuario2 = Usuario(nome="Maria Souza", email="maria@example.com", habilidades="Biologia, Química", nivel="Base")
    db.session.add_all([usuario1, usuario2])

    # Exemplo de Habilidades
    habilidade1 = Habilidade(nome="Física")
    habilidade2 = Habilidade(nome="Química")
    habilidade3 = Habilidade(nome="Programação")
    db.session.add_all([habilidade1, habilidade2, habilidade3])

    # Exemplo de Tarefas
    tarefa1 = Tarefa(descricao="Desenvolver protótipo de reator", complexidade=5, valor=1000, completada=False, projeto_id=projeto1.id)
    tarefa2 = Tarefa(descricao="Realizar testes clínicos", complexidade=8, valor=2000, completada=False, projeto_id=projeto2.id)
    db.session.add_all([tarefa1, tarefa2])

    # Exemplo de Equipes
    equipe1 = Equipe(nome="Equipe Fusão")
    equipe2 = Equipe(nome="Equipe Saúde")
    db.session.add_all([equipe1, equipe2])

    # Exemplo de Avaliação da Equipe
    avaliacao1 = AvaliacaoEquipe(equipe_id=equipe1.id, projeto_id=projeto1.id, avaliador="Dr. Carlos", nota=9.5, comentarios="Ótimo progresso.")
    avaliacao2 = AvaliacaoEquipe(equipe_id=equipe2.id, projeto_id=projeto2.id, avaliador="Dra. Ana", nota=8.0, comentarios="Progresso satisfatório.")
    db.session.add_all([avaliacao1, avaliacao2])

    # Exemplo de Atividades da Equipe
    atividade1 = AtividadeEquipe(equipe_id=equipe1.id, descricao="Reunião inicial para discutir metas.", data_atividade=datetime.utcnow())
    atividade2 = AtividadeEquipe(equipe_id=equipe2.id, descricao="Planejamento dos testes clínicos.", data_atividade=datetime.utcnow())
    db.session.add_all([atividade1, atividade2])

    # Exemplo de Mensagens
    mensagem1 = Mensagem(remetente_id=usuario1.id, destinatario_id=usuario2.id, conteudo="Precisamos discutir a próxima fase do projeto.")
    mensagem2 = Mensagem(remetente_id=usuario2.id, destinatario_id=usuario1.id, conteudo="Concordo, vamos marcar uma reunião.")
    db.session.add_all([mensagem1, mensagem2])

    # Exemplo de Fórum
    forum1 = Forum(titulo="Discussão sobre fusão nuclear", criador_id=usuario1.id, conteudo="Vamos discutir os desafios do desenvolvimento de reatores de fusão.")
    db.session.add(forum1)

    # Confirma as inserções no banco de dados
    db.session.commit()

if __name__ == '__main__':
    seed_data()
