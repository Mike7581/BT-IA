# database.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('memoria.db')
    conn.row_factory = sqlite3.Row  # Permite acesso como dicionário
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        # Tabela de conhecimentos
        conn.execute('''CREATE TABLE IF NOT EXISTS conhecimentos (
                        pergunta TEXT PRIMARY KEY,
                        resposta TEXT,
                        confianca INTEGER DEFAULT 1)''')  # Confiança (1-5)
        
        # Tabela de usuário
        conn.execute('''CREATE TABLE IF NOT EXISTS usuario (
                        id INTEGER PRIMARY KEY,
                        nome TEXT,
                        contexto TEXT)''')
        
        conn.commit()