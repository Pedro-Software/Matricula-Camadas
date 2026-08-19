"""Sistema de matrícula — versão monolítica.

Exercício: separe este arquivo em três camadas (apresentação, negócio,
persistência) sem alterar o comportamento. Nada aqui está errado do ponto de
vista funcional: o problema é que tudo mora no mesmo lugar.

Rodar:  python matricula_monolito.py
"""
from business.services import matricular, cancelar_expiradas
from persistence.database import criar_tabelas, semear
import sqlite3
from datetime import datetime, timedelta

BANCO = "escola.db"
LIMITE_FALTAS = 3
HORAS_PARA_PAGAR = 48

def listar(aluno_id):
    conn = sqlite3.connect(BANCO)
    linhas = conn.execute(
        "SELECT m.turma, t.nome, m.expira_em, m.paga "
        "FROM matricula m JOIN turma t ON t.codigo = m.turma WHERE m.aluno_id = ?",
        (aluno_id,),
    ).fetchall()
    conn.close()
    if not linhas:
        return "Nenhuma matricula encontrada"
    saida = ["Matriculas do aluno %d:" % aluno_id]
    for codigo, nome_turma, expira_em, paga in linhas:
        situacao = "paga" if paga else "aguardando pagamento ate " + expira_em[:16].replace("T", " ")
        saida.append("  - %s (%s) — %s" % (codigo, nome_turma, situacao))
    return "\n".join(saida)


def menu():
    criar_tabelas()
    semear()
    while True:
        print("\n1) Matricular  2) Listar  3) Cancelar expiradas  4) Sair")
        opcao = input("> ").strip()
        if opcao == "1":
            print(matricular(input("id do aluno, codigo da turma: ")))
        elif opcao == "2":
            print(listar(int(input("id do aluno: "))))
        elif opcao == "3":
            print(cancelar_expiradas())
        elif opcao == "4":
            break
        else:
            print("Opcao invalida")


if __name__ == "__main__":
    menu()
