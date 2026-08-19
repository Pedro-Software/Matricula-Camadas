import sqlite3
from datetime import datetime, timedelta

BANCO = "escola.db"


def criar_tabelas():
    conn = sqlite3.connect(BANCO)
    conn.execute("CREATE TABLE IF NOT EXISTS aluno (id INTEGER PRIMARY KEY, nome TEXT, faltas INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS turma (codigo TEXT PRIMARY KEY, nome TEXT, vagas INTEGER)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS matricula ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, aluno_id INTEGER, turma TEXT, "
        "criada_em TEXT, expira_em TEXT, paga INTEGER DEFAULT 0)"
    )
    conn.commit()
    conn.close()


def semear():
    conn = sqlite3.connect(BANCO)
    conn.execute("INSERT OR REPLACE INTO aluno VALUES (42, 'Ana Ribeiro', 1)")
    conn.execute("INSERT OR REPLACE INTO aluno VALUES (43, 'Bruno Lima', 4)")
    conn.execute("INSERT OR REPLACE INTO turma VALUES ('ES2', 'Engenharia de Software II', 2)")
    conn.execute("INSERT OR REPLACE INTO turma VALUES ('AS1', 'Arquitetura de Software', 0)")
    conn.commit()
    conn.close()