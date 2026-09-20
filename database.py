import sqlite3
import sys
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================

def obter_pasta_programa():
    """
    Retorna a pasta principal do sistema.

    Durante o desenvolvimento pelo PyCharm:
    utiliza a pasta onde estão os arquivos .py.

    Quando o sistema estiver convertido para .exe:
    utiliza a pasta onde está localizado o executável.
    """

    if getattr(sys, "frozen", False):

        # Programa executado através do arquivo .exe
        return Path(sys.executable).resolve().parent

    # Programa executado através do Python / PyCharm
    return Path(__file__).resolve().parent


# Pasta principal do sistema
PASTA_PROGRAMA = obter_pasta_programa()

# Pasta onde ficará armazenado o banco de dados
PASTA_DATABASE = PASTA_PROGRAMA / "database"

# Cria a pasta automaticamente caso ela não exista
PASTA_DATABASE.mkdir(
    parents=True,
    exist_ok=True
)

# Arquivo do banco de dados
CAMINHO_BANCO = PASTA_DATABASE / "jornada.db"


# ============================================================
# CONEXÃO COM O BANCO
# ============================================================

def conectar():

    conexao = sqlite3.connect(
        CAMINHO_BANCO
    )

    conexao.row_factory = sqlite3.Row

    return conexao


# ============================================================
# CRIAÇÃO DO BANCO E DAS TABELAS
# ============================================================

def criar_banco():

    conexao = conectar()

    cursor = conexao.cursor()

    # --------------------------------------------------------
    # TABELA DE FUNCIONÁRIOS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            matricula TEXT NOT NULL UNIQUE,
            data_cadastro TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # --------------------------------------------------------
    # TABELA DE JORNADAS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jornadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            entrada TEXT,
            saida_intervalo TEXT,
            retorno_intervalo TEXT,
            saida TEXT,
            FOREIGN KEY (funcionario_id)
                REFERENCES funcionarios(id)
        )
    """)

    conexao.commit()

    conexao.close()


# ============================================================
# CADASTRAR FUNCIONÁRIO
# ============================================================

def cadastrar_funcionario(
    nome,
    cargo,
    matricula,
    data_cadastro
):

    conexao = conectar()

    try:

        conexao.execute("""
            INSERT INTO funcionarios
            (
                nome,
                cargo,
                matricula,
                data_cadastro,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
        """, (
            nome,
            cargo,
            matricula,
            data_cadastro
        ))

        conexao.commit()

        return (
            True,
            "Funcionário cadastrado com sucesso!"
        )

    except sqlite3.IntegrityError:

        return (
            False,
            "A matrícula informada já está cadastrada."
        )

    finally:

        conexao.close()


# ============================================================
# LISTAR FUNCIONÁRIOS
# ============================================================

def listar_funcionarios(
    apenas_ativos=False
):

    conexao = conectar()

    if apenas_ativos:

        registros = conexao.execute("""
            SELECT *
            FROM funcionarios
            WHERE ativo = 1
            ORDER BY nome
        """).fetchall()

    else:

        registros = conexao.execute("""
            SELECT *
            FROM funcionarios
            ORDER BY nome
        """).fetchall()

    conexao.close()

    return registros


# ============================================================
# BUSCAR FUNCIONÁRIO
# ============================================================

def buscar_funcionario(
    funcionario_id
):

    conexao = conectar()

    registro = conexao.execute("""
        SELECT *
        FROM funcionarios
        WHERE id = ?
    """, (
        funcionario_id,
    )).fetchone()

    conexao.close()

    return registro


# ============================================================
# ALTERAR FUNCIONÁRIO
# ============================================================

def alterar_funcionario(
    funcionario_id,
    nome,
    cargo,
    matricula
):

    conexao = conectar()

    try:

        conexao.execute("""
            UPDATE funcionarios
            SET
                nome = ?,
                cargo = ?,
                matricula = ?
            WHERE id = ?
        """, (
            nome,
            cargo,
            matricula,
            funcionario_id
        ))

        conexao.commit()

        return (
            True,
            "Funcionário atualizado com sucesso!"
        )

    except sqlite3.IntegrityError:

        return (
            False,
            "A matrícula informada já está cadastrada."
        )

    finally:

        conexao.close()


# ============================================================
# ATIVAR / DESATIVAR FUNCIONÁRIO
# ============================================================

def alterar_status_funcionario(
    funcionario_id,
    ativo
):

    conexao = conectar()

    conexao.execute("""
        UPDATE funcionarios
        SET ativo = ?
        WHERE id = ?
    """, (
        1 if ativo else 0,
        funcionario_id
    ))

    conexao.commit()

    conexao.close()


# ============================================================
# BUSCAR JORNADA DO DIA
# ============================================================

def buscar_jornada_do_dia(
    funcionario_id,
    data
):

    conexao = conectar()

    registro = conexao.execute("""
        SELECT *
        FROM jornadas
        WHERE funcionario_id = ?
        AND data = ?
    """, (
        funcionario_id,
        data
    )).fetchone()

    conexao.close()

    return registro


# ============================================================
# CRIAR JORNADA
# ============================================================

def criar_jornada(
    funcionario_id,
    data,
    entrada
):

    conexao = conectar()

    cursor = conexao.execute("""
        INSERT INTO jornadas
        (
            funcionario_id,
            data,
            entrada
        )
        VALUES (?, ?, ?)
    """, (
        funcionario_id,
        data,
        entrada
    ))

    conexao.commit()

    jornada_id = cursor.lastrowid

    conexao.close()

    return jornada_id


# ============================================================
# ATUALIZAR JORNADA
# ============================================================

def atualizar_jornada(
    jornada_id,
    campo,
    horario
):

    campos_permitidos = {
        "entrada",
        "saida_intervalo",
        "retorno_intervalo",
        "saida"
    }

    if campo not in campos_permitidos:

        raise ValueError(
            "Campo de jornada inválido."
        )

    conexao = conectar()

    conexao.execute(
        f"""
        UPDATE jornadas
        SET {campo} = ?
        WHERE id = ?
        """,
        (
            horario,
            jornada_id
        )
    )

    conexao.commit()

    conexao.close()


# ============================================================
# LISTAR JORNADAS
# ============================================================

def listar_jornadas(
    data_inicio=None,
    data_fim=None,
    funcionario_id=None
):

    conexao = conectar()

    sql = """
        SELECT
            jornadas.*,
            funcionarios.nome,
            funcionarios.cargo,
            funcionarios.matricula

        FROM jornadas

        INNER JOIN funcionarios
            ON funcionarios.id =
               jornadas.funcionario_id

        WHERE 1 = 1
    """

    parametros = []

    # --------------------------------------------------------
    # FILTRO POR DATA INICIAL
    # --------------------------------------------------------

    if data_inicio:

        sql += """
            AND jornadas.data >= ?
        """

        parametros.append(
            data_inicio
        )

    # --------------------------------------------------------
    # FILTRO POR DATA FINAL
    # --------------------------------------------------------

    if data_fim:

        sql += """
            AND jornadas.data <= ?
        """

        parametros.append(
            data_fim
        )

    # --------------------------------------------------------
    # FILTRO POR FUNCIONÁRIO
    # --------------------------------------------------------

    if funcionario_id:

        sql += """
            AND jornadas.funcionario_id = ?
        """

        parametros.append(
            funcionario_id
        )

    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    sql += """
        ORDER BY
            jornadas.data DESC,
            funcionarios.nome
    """

    registros = conexao.execute(
        sql,
        parametros
    ).fetchall()

    conexao.close()

    return registros


# ============================================================
# INICIALIZAÇÃO AUTOMÁTICA
# ============================================================

criar_banco()