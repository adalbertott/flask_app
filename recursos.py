from flask_sqlalchemy import SQLAlchemy
from models import Projeto

db = SQLAlchemy()

# Função para liberar recursos de acordo com o progresso da fase
def liberar_recursos(projeto_id, progresso_fase):
    projeto = Projeto.query.get(projeto_id)
    
    if projeto:
        if projeto.status == 'Aprovado' and projeto.fase <= 3:
            total_fase = projeto.recursos_alocados / 3  # Distribui igualmente entre as 3 fases

            # Calcula a liberação proporcional ao progresso
            recursos_liberados = total_fase * (progresso_fase / 100)

            # Atualiza o progresso e recursos alocados
            projeto.recursos_alocados += recursos_liberados
            db.session.commit()
            return {"message": f"Recursos liberados: {recursos_liberados}"}

    return {"message": "Erro ao liberar recursos"}

from flask_sqlalchemy import SQLAlchemy
from models import Projeto, Tarefa

db = SQLAlchemy()

# Função para converter tarefas em moeda
def converter_tarefas_para_moeda(projeto_id, tarefas_completadas):
    projeto = Projeto.query.get(projeto_id)
    
    if projeto:
        # Exemplo de conversão: 1 tarefa completada = 100 unidades de moeda
        moeda_por_tarefa = 100
        moeda_total = tarefas_completadas * moeda_por_tarefa

        # Atribuir as moedas ao projeto ou ao usuário
        projeto.contribuicao_financeira += moeda_total
        db.session.commit()
        
        return {"moeda_total": moeda_total}
    
    return {"message": "Erro ao converter tarefas para moeda"}

# Exemplo de uso da função:
# Você pode passar a quantidade de tarefas completadas para converter em moeda
resultado = converter_tarefas_para_moeda(projeto_id=1, tarefas_completadas=5)
print(resultado)
