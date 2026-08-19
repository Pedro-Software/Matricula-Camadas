"""Sistema de matrícula — versão monolítica.

Exercício: separe este arquivo em três camadas (apresentação, negócio,
persistência) sem alterar o comportamento. Nada aqui está errado do ponto de
vista funcional: o problema é que tudo mora no mesmo lugar.

Rodar:  python matricula_monolito.py
"""
import sqlite3
from datetime import datetime, timedelta
from persistence.database import criar_tabelas, semear

BANCO = "escola.db"
LIMITE_FALTAS = 3
HORAS_PARA_PAGAR = 48

def matricular(entrada_usuario):
    """Recebe o texto digitado no formulário, valida, aplica as regras e grava."""
    partes = [p.strip() for p in entrada_usuario.split(",")]
    if len(partes) != 2:
        return "Formato invalido. Use: <id do aluno>, <codigo da turma>"
    if not partes[0].isdigit():
        return "O id do aluno precisa ser um numero"
    aluno_id = int(partes[0])
    turma = partes[1].upper()

    conn = sqlite3.connect(BANCO)

    linha_aluno = conn.execute("SELECT nome, faltas FROM aluno WHERE id = ?", (aluno_id,)).fetchone()
    if linha_aluno is None:
        conn.close()
        return "Aluno %d nao encontrado" % aluno_id
    nome, faltas = linha_aluno

    if faltas >= LIMITE_FALTAS:
        conn.close()
        return "%s tem %d faltas e nao pode se matricular" % (nome, faltas)

    linha_turma = conn.execute("SELECT nome, vagas FROM turma WHERE codigo = ?", (turma,)).fetchone()
    if linha_turma is None:
        conn.close()
        return "Turma %s nao existe" % turma
    nome_turma, vagas = linha_turma

    if vagas <= 0:
        conn.close()
        return "Sem vagas em %s" % nome_turma

    ja_matriculado = conn.execute(
        "SELECT 1 FROM matricula WHERE aluno_id = ? AND turma = ?", (aluno_id, turma)
    ).fetchone()
    if ja_matriculado:
        conn.close()
        return "%s ja esta matriculado em %s" % (nome, nome_turma)

    agora = datetime.now()
    expira = agora + timedelta(hours=HORAS_PARA_PAGAR)
    conn.execute(
        "INSERT INTO matricula (aluno_id, turma, criada_em, expira_em) VALUES (?, ?, ?, ?)",
        (aluno_id, turma, agora.isoformat(), expira.isoformat()),
    )
    conn.execute("UPDATE turma SET vagas = vagas - 1 WHERE codigo = ?", (turma,))
    conn.commit()
    conn.close()

    return "Matricula de %s em %s confirmada. Pague ate %s" % (
        nome,
        nome_turma,
        expira.strftime("%d/%m/%Y as %H:%M"),
    )


def cancelar_expiradas():
    conn = sqlite3.connect(BANCO)
    agora = datetime.now().isoformat()
    expiradas = conn.execute(
        "SELECT id, turma FROM matricula WHERE paga = 0 AND expira_em < ?", (agora,)
    ).fetchall()
    for matricula_id, turma in expiradas:
        conn.execute("DELETE FROM matricula WHERE id = ?", (matricula_id,))
        conn.execute("UPDATE turma SET vagas = vagas + 1 WHERE codigo = ?", (turma,))
    conn.commit()
    conn.close()
    return "%d matricula(s) expirada(s) cancelada(s)" % len(expiradas)


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
