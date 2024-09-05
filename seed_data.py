from app import db
from models import GrandeProblema

def seed_data():
    problema = GrandeProblema(nome="Problema Inicial", descricao="Problema de exemplo")
    db.session.add(problema)
    db.session.commit()

if __name__ == '__main__':
    seed_data()
