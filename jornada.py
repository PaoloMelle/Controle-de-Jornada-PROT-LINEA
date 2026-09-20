import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

import database


# ============================================================
# CORES DO SISTEMA
# ============================================================

COR_PRINCIPAL = "#11BAA9"
COR_HOVER = "#0E9E90"
COR_INATIVO = "#6B7280"
COR_SUCESSO = "#16A34A"


class TelaJornada(ctk.CTkFrame):
    """
    Tela responsável pelo registro da jornada dos colaboradores
    da PROT LINEA.
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

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        titulo = ctk.CTkLabel(
            self,
            text="Registrar Jornada",
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
                "Registre automaticamente os horários de entrada, "
                "intervalo, retorno e saída."
            ),
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # CARD DE SELEÇÃO
        # ----------------------------------------------------

        card_selecao = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        card_selecao.pack(
            fill="x",
            pady=(0, 20)
        )

        label_funcionario = ctk.CTkLabel(
            card_selecao,
            text="Funcionário",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )

        label_funcionario.pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        self.combo_funcionarios = ctk.CTkComboBox(
            card_selecao,
            values=["Nenhum funcionário cadastrado"],
            height=42,
            state="readonly",
            command=self.selecionar_funcionario
        )

        self.combo_funcionarios.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # INFORMAÇÕES DO DIA
        # ----------------------------------------------------

        self.card_status = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        self.card_status.pack(
            fill="x",
            pady=(0, 20)
        )

        self.label_data = ctk.CTkLabel(
            self.card_status,
            text="Data: --/--/----",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        )

        self.label_data.pack(
            anchor="w",
            padx=20,
            pady=(18, 6)
        )

        self.label_status = ctk.CTkLabel(
            self.card_status,
            text="Selecione um funcionário para visualizar a jornada.",
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        self.label_status.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        # ----------------------------------------------------
        # HORÁRIOS REGISTRADOS
        # ----------------------------------------------------

        self.card_horarios = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        self.card_horarios.pack(
            fill="x",
            pady=(0, 20)
        )

        titulo_horarios = ctk.CTkLabel(
            self.card_horarios,
            text="Horários de hoje",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_horarios.pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        frame_horarios = ctk.CTkFrame(
            self.card_horarios,
            fg_color="transparent"
        )

        frame_horarios.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        for coluna in range(4):
            frame_horarios.grid_columnconfigure(
                coluna,
                weight=1
            )

        self.label_entrada = self.criar_card_horario(
            frame_horarios,
            "Entrada",
            0
        )

        self.label_saida_intervalo = self.criar_card_horario(
            frame_horarios,
            "Saída intervalo",
            1
        )

        self.label_retorno = self.criar_card_horario(
            frame_horarios,
            "Retorno",
            2
        )

        self.label_saida = self.criar_card_horario(
            frame_horarios,
            "Saída final",
            3
        )

        # ----------------------------------------------------
        # BOTÃO PRINCIPAL
        # ----------------------------------------------------

        self.botao_registrar = ctk.CTkButton(
            self,
            text="Selecione um funcionário",
            height=55,
            fg_color=COR_INATIVO,
            hover_color=COR_INATIVO,
            state="disabled",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            command=self.registrar_proximo_horario
        )

        self.botao_registrar.pack(
            fill="x",
            pady=(5, 0)
        )

    # ========================================================
    # CARD DE HORÁRIO
    # ========================================================

    def criar_card_horario(self, parent, titulo, coluna):

        frame = ctk.CTkFrame(
            parent,
            corner_radius=10
        )

        frame.grid(
            row=0,
            column=coluna,
            padx=5,
            sticky="ew"
        )

        label_titulo = ctk.CTkLabel(
            frame,
            text=titulo,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="gray"
        )

        label_titulo.pack(
            pady=(12, 3)
        )

        label_horario = ctk.CTkLabel(
            frame,
            text="--:--:--",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        label_horario.pack(
            pady=(0, 12)
        )

        return label_horario

    # ========================================================
    # FUNCIONÁRIOS
    # ========================================================

    def carregar_funcionarios(self):

        self.funcionarios = database.listar_funcionarios(
            apenas_ativos=True
        )

        if not self.funcionarios:

            self.combo_funcionarios.configure(
                values=["Nenhum funcionário ativo"]
            )

            self.combo_funcionarios.set(
                "Nenhum funcionário ativo"
            )

            return

        nomes = []

        for funcionario in self.funcionarios:

            nomes.append(
                f'{funcionario["matricula"]} - {funcionario["nome"]}'
            )

        self.combo_funcionarios.configure(
            values=nomes
        )

        self.combo_funcionarios.set(
            "Selecione um funcionário"
        )

    # ========================================================
    # SELECIONAR FUNCIONÁRIO
    # ========================================================

    def selecionar_funcionario(self, escolha):

        for funcionario in self.funcionarios:

            texto = (
                f'{funcionario["matricula"]} - '
                f'{funcionario["nome"]}'
            )

            if texto == escolha:

                self.funcionario_selecionado_id = funcionario["id"]

                self.atualizar_jornada()

                break

    # ========================================================
    # ATUALIZAR JORNADA
    # ========================================================

    def atualizar_jornada(self):

        if self.funcionario_selecionado_id is None:
            return

        hoje_banco = datetime.now().strftime("%Y-%m-%d")
        hoje_tela = datetime.now().strftime("%d/%m/%Y")

        self.label_data.configure(
            text=f"Data: {hoje_tela}"
        )

        jornada = database.buscar_jornada_do_dia(
            self.funcionario_selecionado_id,
            hoje_banco
        )

        # ----------------------------------------------------
        # SEM JORNADA AINDA
        # ----------------------------------------------------

        if jornada is None:

            self.limpar_horarios()

            self.label_status.configure(
                text="Nenhum horário registrado hoje."
            )

            self.configurar_botao(
                "Registrar Entrada"
            )

            return

        # ----------------------------------------------------
        # EXIBE HORÁRIOS
        # ----------------------------------------------------

        self.label_entrada.configure(
            text=jornada["entrada"] or "--:--:--"
        )

        self.label_saida_intervalo.configure(
            text=jornada["saida_intervalo"] or "--:--:--"
        )

        self.label_retorno.configure(
            text=jornada["retorno_intervalo"] or "--:--:--"
        )

        self.label_saida.configure(
            text=jornada["saida"] or "--:--:--"
        )

        # ----------------------------------------------------
        # DEFINE A PRÓXIMA AÇÃO
        # ----------------------------------------------------

        if not jornada["entrada"]:

            self.configurar_botao(
                "Registrar Entrada"
            )

            self.label_status.configure(
                text="Aguardando registro de entrada."
            )

        elif not jornada["saida_intervalo"]:

            self.configurar_botao(
                "Registrar Saída para Intervalo"
            )

            self.label_status.configure(
                text="Jornada iniciada."
            )

        elif not jornada["retorno_intervalo"]:

            self.configurar_botao(
                "Registrar Retorno do Intervalo"
            )

            self.label_status.configure(
                text="Funcionário em intervalo."
            )

        elif not jornada["saida"]:

            self.configurar_botao(
                "Registrar Saída Final"
            )

            self.label_status.configure(
                text="Funcionário retornou do intervalo."
            )

        else:

            self.botao_registrar.configure(
                text="Jornada concluída",
                state="disabled",
                fg_color=COR_SUCESSO,
                hover_color=COR_SUCESSO
            )

            self.label_status.configure(
                text="Jornada de hoje concluída."
            )

    # ========================================================
    # CONFIGURAR BOTÃO
    # ========================================================

    def configurar_botao(self, texto):

        self.botao_registrar.configure(
            text=texto,
            state="normal",
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER
        )

    # ========================================================
    # REGISTRAR HORÁRIO
    # ========================================================

    def registrar_proximo_horario(self):

        if self.funcionario_selecionado_id is None:

            messagebox.showwarning(
                "Funcionário",
                "Selecione um funcionário."
            )

            return

        agora = datetime.now()

        data_atual = agora.strftime("%Y-%m-%d")
        horario_atual = agora.strftime("%H:%M:%S")

        jornada = database.buscar_jornada_do_dia(
            self.funcionario_selecionado_id,
            data_atual
        )

        # ----------------------------------------------------
        # REGISTRA ENTRADA
        # ----------------------------------------------------

        if jornada is None:

            database.criar_jornada(
                self.funcionario_selecionado_id,
                data_atual,
                horario_atual
            )

            messagebox.showinfo(
                "Entrada registrada",
                f"Entrada registrada às {horario_atual}."
            )

        # ----------------------------------------------------
        # REGISTRA SAÍDA PARA INTERVALO
        # ----------------------------------------------------

        elif not jornada["saida_intervalo"]:

            database.atualizar_jornada(
                jornada["id"],
                "saida_intervalo",
                horario_atual
            )

            messagebox.showinfo(
                "Intervalo registrado",
                f"Saída para intervalo registrada às {horario_atual}."
            )

        # ----------------------------------------------------
        # REGISTRA RETORNO
        # ----------------------------------------------------

        elif not jornada["retorno_intervalo"]:

            database.atualizar_jornada(
                jornada["id"],
                "retorno_intervalo",
                horario_atual
            )

            messagebox.showinfo(
                "Retorno registrado",
                f"Retorno do intervalo registrado às {horario_atual}."
            )

        # ----------------------------------------------------
        # REGISTRA SAÍDA FINAL
        # ----------------------------------------------------

        elif not jornada["saida"]:

            database.atualizar_jornada(
                jornada["id"],
                "saida",
                horario_atual
            )

            messagebox.showinfo(
                "Saída registrada",
                f"Saída final registrada às {horario_atual}."
            )

        else:

            messagebox.showinfo(
                "Jornada concluída",
                "A jornada deste funcionário já foi concluída hoje."
            )

        self.atualizar_jornada()

    # ========================================================
    # LIMPAR HORÁRIOS
    # ========================================================

    def limpar_horarios(self):

        self.label_entrada.configure(
            text="--:--:--"
        )

        self.label_saida_intervalo.configure(
            text="--:--:--"
        )

        self.label_retorno.configure(
            text="--:--:--"
        )

        self.label_saida.configure(
            text="--:--:--"
        )