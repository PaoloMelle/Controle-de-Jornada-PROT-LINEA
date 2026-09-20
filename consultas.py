import customtkinter as ctk
from datetime import datetime

import database


# ============================================================
# CORES DO SISTEMA
# ============================================================

COR_PRINCIPAL = "#11BAA9"
COR_HOVER = "#0E9E90"


class TelaConsultas(ctk.CTkFrame):
    """
    Tela responsável pela consulta dos registros de jornada
    dos colaboradores da PROT LINEA.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.funcionarios = []
        self.funcionario_selecionado_id = None

        self.pack(
            fill="both",
            expand=True
        )

        self.criar_interface()
        self.carregar_funcionarios()
        self.consultar()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        titulo = ctk.CTkLabel(
            self,
            text="Consultas",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        titulo.pack(
            anchor="w",
            pady=(5, 3)
        )

        subtitulo = ctk.CTkLabel(
            self,
            text=(
                "Consulte os registros de jornada por funcionário "
                "e período."
            ),
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # FILTROS
        # ----------------------------------------------------

        frame_filtros = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        frame_filtros.pack(
            fill="x",
            pady=(0, 20)
        )

        titulo_filtros = ctk.CTkLabel(
            frame_filtros,
            text="Filtros de consulta",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_filtros.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        frame_campos = ctk.CTkFrame(
            frame_filtros,
            fg_color="transparent"
        )

        frame_campos.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        frame_campos.grid_columnconfigure(0, weight=3)
        frame_campos.grid_columnconfigure(1, weight=2)
        frame_campos.grid_columnconfigure(2, weight=2)

        # Funcionário
        self.combo_funcionarios = ctk.CTkComboBox(
            frame_campos,
            values=["Todos os funcionários"],
            height=40,
            state="readonly",
            command=self.selecionar_funcionario
        )

        self.combo_funcionarios.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew"
        )

        self.combo_funcionarios.set(
            "Todos os funcionários"
        )

        # Data inicial
        self.entry_data_inicio = ctk.CTkEntry(
            frame_campos,
            placeholder_text="Data inicial (dd/mm/aaaa)",
            height=40
        )

        self.entry_data_inicio.grid(
            row=0,
            column=1,
            padx=10,
            sticky="ew"
        )

        # Data final
        self.entry_data_fim = ctk.CTkEntry(
            frame_campos,
            placeholder_text="Data final (dd/mm/aaaa)",
            height=40
        )

        self.entry_data_fim.grid(
            row=0,
            column=2,
            padx=(10, 0),
            sticky="ew"
        )

        # ----------------------------------------------------
        # BOTÕES DOS FILTROS
        # ----------------------------------------------------

        frame_botoes = ctk.CTkFrame(
            frame_filtros,
            fg_color="transparent"
        )

        frame_botoes.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        botao_consultar = ctk.CTkButton(
            frame_botoes,
            text="Consultar",
            width=120,
            height=40,
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER,
            command=self.consultar
        )

        botao_consultar.pack(
            side="left"
        )

        botao_limpar = ctk.CTkButton(
            frame_botoes,
            text="Limpar filtros",
            width=120,
            height=40,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.limpar_filtros
        )

        botao_limpar.pack(
            side="left",
            padx=10
        )

        # ----------------------------------------------------
        # CABEÇALHO DOS RESULTADOS
        # ----------------------------------------------------

        frame_cabecalho = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame_cabecalho.pack(
            fill="x",
            pady=(0, 8)
        )

        titulo_resultados = ctk.CTkLabel(
            frame_cabecalho,
            text="Registros encontrados",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_resultados.pack(
            side="left"
        )

        self.label_total = ctk.CTkLabel(
            frame_cabecalho,
            text="0 registro(s)",
            text_color="gray"
        )

        self.label_total.pack(
            side="right"
        )

        # ----------------------------------------------------
        # LISTA DE RESULTADOS
        # ----------------------------------------------------

        self.frame_resultados = ctk.CTkScrollableFrame(
            self,
            corner_radius=12
        )

        self.frame_resultados.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # CARREGAR FUNCIONÁRIOS
    # ========================================================

    def carregar_funcionarios(self):

        self.funcionarios = database.listar_funcionarios()

        valores = [
            "Todos os funcionários"
        ]

        for funcionario in self.funcionarios:

            valores.append(
                f'{funcionario["matricula"]} - {funcionario["nome"]}'
            )

        self.combo_funcionarios.configure(
            values=valores
        )

    # ========================================================
    # SELECIONAR FUNCIONÁRIO
    # ========================================================

    def selecionar_funcionario(self, escolha):

        if escolha == "Todos os funcionários":

            self.funcionario_selecionado_id = None
            return

        for funcionario in self.funcionarios:

            texto = (
                f'{funcionario["matricula"]} - '
                f'{funcionario["nome"]}'
            )

            if texto == escolha:

                self.funcionario_selecionado_id = funcionario["id"]
                break

    # ========================================================
    # CONVERTER DATA
    # ========================================================

    def converter_data_para_banco(self, data_texto):

        if not data_texto:
            return None

        try:

            data = datetime.strptime(
                data_texto,
                "%d/%m/%Y"
            )

            return data.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            return None

    # ========================================================
    # CALCULAR DIFERENÇA DE HORÁRIOS
    # ========================================================

    def calcular_duracao(self, inicio, fim):

        if not inicio or not fim:
            return "--"

        try:

            horario_inicio = datetime.strptime(
                inicio,
                "%H:%M:%S"
            )

            horario_fim = datetime.strptime(
                fim,
                "%H:%M:%S"
            )

            diferenca = horario_fim - horario_inicio

            segundos = int(
                diferenca.total_seconds()
            )

            if segundos < 0:
                return "--"

            horas = segundos // 3600
            minutos = (segundos % 3600) // 60

            return f"{horas:02d}h {minutos:02d}min"

        except ValueError:

            return "--"

    # ========================================================
    # CALCULAR TOTAL TRABALHADO
    # ========================================================

    def calcular_total_trabalhado(self, registro):

        entrada = registro["entrada"]
        saida_intervalo = registro["saida_intervalo"]
        retorno_intervalo = registro["retorno_intervalo"]
        saida_final = registro["saida"]

        if not entrada or not saida_final:
            return "--"

        try:

            entrada_dt = datetime.strptime(
                entrada,
                "%H:%M:%S"
            )

            saida_dt = datetime.strptime(
                saida_final,
                "%H:%M:%S"
            )

            total = (
                saida_dt - entrada_dt
            ).total_seconds()

            # Se houver intervalo completo,
            # ele é descontado da jornada.
            if saida_intervalo and retorno_intervalo:

                inicio_intervalo = datetime.strptime(
                    saida_intervalo,
                    "%H:%M:%S"
                )

                fim_intervalo = datetime.strptime(
                    retorno_intervalo,
                    "%H:%M:%S"
                )

                intervalo = (
                    fim_intervalo -
                    inicio_intervalo
                ).total_seconds()

                total -= intervalo

            if total < 0:
                return "--"

            horas = int(total) // 3600
            minutos = (
                int(total) % 3600
            ) // 60

            return f"{horas:02d}h {minutos:02d}min"

        except ValueError:

            return "--"

    # ========================================================
    # CONSULTAR
    # ========================================================

    def consultar(self):

        data_inicio_texto = (
            self.entry_data_inicio.get().strip()
        )

        data_fim_texto = (
            self.entry_data_fim.get().strip()
        )

        data_inicio = self.converter_data_para_banco(
            data_inicio_texto
        )

        data_fim = self.converter_data_para_banco(
            data_fim_texto
        )

        # ----------------------------------------------------
        # VALIDAÇÃO DAS DATAS
        # ----------------------------------------------------

        if data_inicio_texto and not data_inicio:

            self.exibir_mensagem_lista(
                "Data inicial inválida. Utilize dd/mm/aaaa."
            )

            return

        if data_fim_texto and not data_fim:

            self.exibir_mensagem_lista(
                "Data final inválida. Utilize dd/mm/aaaa."
            )

            return

        registros = database.listar_jornadas(
            data_inicio=data_inicio,
            data_fim=data_fim,
            funcionario_id=self.funcionario_selecionado_id
        )

        # Limpa os resultados anteriores
        for widget in self.frame_resultados.winfo_children():

            widget.destroy()

        self.label_total.configure(
            text=f"{len(registros)} registro(s)"
        )

        if not registros:

            self.exibir_mensagem_lista(
                "Nenhum registro encontrado."
            )

            return

        # ----------------------------------------------------
        # EXIBE CADA REGISTRO
        # ----------------------------------------------------

        for registro in registros:

            self.criar_card_registro(
                registro
            )

    # ========================================================
    # CRIAR CARD DO REGISTRO
    # ========================================================

    def criar_card_registro(self, registro):

        card = ctk.CTkFrame(
            self.frame_resultados,
            corner_radius=10
        )

        card.pack(
            fill="x",
            padx=5,
            pady=5
        )

        # ----------------------------------------------------
        # CABEÇALHO
        # ----------------------------------------------------

        frame_topo = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        frame_topo.pack(
            fill="x",
            padx=15,
            pady=(12, 5)
        )

        nome = ctk.CTkLabel(
            frame_topo,
            text=registro["nome"],
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )

        nome.pack(
            side="left"
        )

        data_formatada = datetime.strptime(
            registro["data"],
            "%Y-%m-%d"
        ).strftime(
            "%d/%m/%Y"
        )

        data_label = ctk.CTkLabel(
            frame_topo,
            text=data_formatada,
            text_color="gray"
        )

        data_label.pack(
            side="right"
        )

        # ----------------------------------------------------
        # DADOS DO FUNCIONÁRIO
        # ----------------------------------------------------

        dados = ctk.CTkLabel(
            card,
            text=(
                f'Matrícula: {registro["matricula"]}    |    '
                f'Cargo: {registro["cargo"]}'
            ),
            text_color="gray"
        )

        dados.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # HORÁRIOS
        # ----------------------------------------------------

        frame_horarios = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        frame_horarios.pack(
            fill="x",
            padx=15,
            pady=(0, 8)
        )

        texto_horarios = (
            f'Entrada: {registro["entrada"] or "--"}     |     '
            f'Saída intervalo: {registro["saida_intervalo"] or "--"}     |     '
            f'Retorno: {registro["retorno_intervalo"] or "--"}     |     '
            f'Saída: {registro["saida"] or "--"}'
        )

        horarios = ctk.CTkLabel(
            frame_horarios,
            text=texto_horarios,
            font=ctk.CTkFont(size=13)
        )

        horarios.pack(
            anchor="w"
        )

        # ----------------------------------------------------
        # CÁLCULOS
        # ----------------------------------------------------

        duracao_intervalo = self.calcular_duracao(
            registro["saida_intervalo"],
            registro["retorno_intervalo"]
        )

        total_trabalhado = self.calcular_total_trabalhado(
            registro
        )

        frame_calculos = ctk.CTkFrame(
            card,
            corner_radius=8
        )

        frame_calculos.pack(
            fill="x",
            padx=15,
            pady=(5, 12)
        )

        intervalo = ctk.CTkLabel(
            frame_calculos,
            text=f"Intervalo: {duracao_intervalo}",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        intervalo.pack(
            side="left",
            padx=15,
            pady=10
        )

        total = ctk.CTkLabel(
            frame_calculos,
            text=f"Total trabalhado: {total_trabalhado}",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color=COR_PRINCIPAL
        )

        total.pack(
            side="right",
            padx=15,
            pady=10
        )

    # ========================================================
    # MENSAGEM NA LISTA
    # ========================================================

    def exibir_mensagem_lista(self, mensagem):

        for widget in self.frame_resultados.winfo_children():

            widget.destroy()

        label = ctk.CTkLabel(
            self.frame_resultados,
            text=mensagem,
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        label.pack(
            pady=40
        )

    # ========================================================
    # LIMPAR FILTROS
    # ========================================================

    def limpar_filtros(self):

        self.combo_funcionarios.set(
            "Todos os funcionários"
        )

        self.funcionario_selecionado_id = None

        self.entry_data_inicio.delete(
            0,
            "end"
        )

        self.entry_data_fim.delete(
            0,
            "end"
        )

        # Limpa os resultados exibidos
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        self.label_total.configure(
            text="0 registro(s)"
        )

        self.exibir_mensagem_lista(
            "Utilize os filtros acima e clique em Consultar."
        )