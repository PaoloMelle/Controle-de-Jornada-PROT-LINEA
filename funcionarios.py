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


class TelaFuncionarios(ctk.CTkFrame):
    """
    Tela responsável pelo cadastro e gerenciamento
    dos funcionários da PROT LINEA.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.funcionario_em_edicao = None

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

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = ctk.CTkLabel(
            self,
            text="Funcionários",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        titulo.pack(
            anchor="w",
            pady=(5, 0)
        )

        subtitulo = ctk.CTkLabel(
            self,
            text="Cadastro e gerenciamento dos colaboradores da PROT LINEA.",
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # FORMULÁRIO
        # ----------------------------------------------------

        self.frame_formulario = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        self.frame_formulario.pack(
            fill="x",
            pady=(0, 20)
        )

        titulo_formulario = ctk.CTkLabel(
            self.frame_formulario,
            text="Cadastrar funcionário",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_formulario.pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        # Frame dos campos
        frame_campos = ctk.CTkFrame(
            self.frame_formulario,
            fg_color="transparent"
        )

        frame_campos.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        frame_campos.grid_columnconfigure(0, weight=3)
        frame_campos.grid_columnconfigure(1, weight=2)
        frame_campos.grid_columnconfigure(2, weight=1)

        # Nome
        self.entry_nome = ctk.CTkEntry(
            frame_campos,
            placeholder_text="Nome completo",
            height=40
        )

        self.entry_nome.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew"
        )

        # Cargo
        self.entry_cargo = ctk.CTkEntry(
            frame_campos,
            placeholder_text="Cargo",
            height=40
        )

        self.entry_cargo.grid(
            row=0,
            column=1,
            padx=10,
            sticky="ew"
        )

        # Matrícula
        self.entry_matricula = ctk.CTkEntry(
            frame_campos,
            placeholder_text="Matrícula",
            height=40
        )

        self.entry_matricula.grid(
            row=0,
            column=2,
            padx=(10, 0),
            sticky="ew"
        )

        # ----------------------------------------------------
        # BOTÕES DO FORMULÁRIO
        # ----------------------------------------------------

        frame_botoes = ctk.CTkFrame(
            self.frame_formulario,
            fg_color="transparent"
        )

        frame_botoes.pack(
            fill="x",
            padx=20,
            pady=(5, 18)
        )

        self.botao_salvar = ctk.CTkButton(
            frame_botoes,
            text="Cadastrar",
            width=130,
            height=40,
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER,
            command=self.salvar_funcionario
        )

        self.botao_salvar.pack(
            side="left"
        )

        self.botao_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar edição",
            width=130,
            height=40,
            fg_color=COR_INATIVO,
            hover_color="#4B5563",
            command=self.cancelar_edicao
        )

        # O botão cancelar só aparece durante edição.

        # ----------------------------------------------------
        # LISTAGEM
        # ----------------------------------------------------

        frame_cabecalho_lista = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame_cabecalho_lista.pack(
            fill="x",
            pady=(0, 8)
        )

        titulo_lista = ctk.CTkLabel(
            frame_cabecalho_lista,
            text="Funcionários cadastrados",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_lista.pack(
            side="left"
        )

        self.label_total = ctk.CTkLabel(
            frame_cabecalho_lista,
            text="",
            text_color="gray"
        )

        self.label_total.pack(
            side="right"
        )

        self.frame_lista = ctk.CTkScrollableFrame(
            self,
            corner_radius=12
        )

        self.frame_lista.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # CADASTRAR / ALTERAR
    # ========================================================

    def salvar_funcionario(self):

        nome = self.entry_nome.get().strip()
        cargo = self.entry_cargo.get().strip()
        matricula = self.entry_matricula.get().strip()

        # Validação dos campos
        if not nome or not cargo or not matricula:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha o nome, cargo e matrícula."
            )
            return

        # ----------------------------------------------------
        # NOVO FUNCIONÁRIO
        # ----------------------------------------------------

        if self.funcionario_em_edicao is None:

            data_cadastro = datetime.now().strftime("%Y-%m-%d")

            sucesso, mensagem = database.cadastrar_funcionario(
                nome,
                cargo,
                matricula,
                data_cadastro
            )

        # ----------------------------------------------------
        # ALTERAÇÃO
        # ----------------------------------------------------

        else:

            sucesso, mensagem = database.alterar_funcionario(
                self.funcionario_em_edicao,
                nome,
                cargo,
                matricula
            )

        if sucesso:

            messagebox.showinfo(
                "Sucesso",
                mensagem
            )

            self.limpar_campos()
            self.carregar_funcionarios()

        else:

            messagebox.showerror(
                "Erro",
                mensagem
            )

    # ========================================================
    # CARREGAR FUNCIONÁRIOS
    # ========================================================

    def carregar_funcionarios(self):

        # Remove os registros exibidos anteriormente.
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        funcionarios = database.listar_funcionarios()

        self.label_total.configure(
            text=f"{len(funcionarios)} cadastrado(s)"
        )

        # Caso ainda não exista nenhum funcionário.
        if not funcionarios:

            vazio = ctk.CTkLabel(
                self.frame_lista,
                text="Nenhum funcionário cadastrado.",
                font=ctk.CTkFont(size=15),
                text_color="gray"
            )

            vazio.pack(
                pady=40
            )

            return

        # ----------------------------------------------------
        # CRIA UM CARD PARA CADA FUNCIONÁRIO
        # ----------------------------------------------------

        for funcionario in funcionarios:

            card = ctk.CTkFrame(
                self.frame_lista,
                corner_radius=10
            )

            card.pack(
                fill="x",
                padx=5,
                pady=5
            )

            card.grid_columnconfigure(0, weight=1)

            # Nome
            nome = ctk.CTkLabel(
                card,
                text=funcionario["nome"],
                font=ctk.CTkFont(
                    size=16,
                    weight="bold"
                )
            )

            nome.grid(
                row=0,
                column=0,
                sticky="w",
                padx=15,
                pady=(12, 2)
            )

            # Dados
            dados = ctk.CTkLabel(
                card,
                text=(
                    f'Cargo: {funcionario["cargo"]}    |    '
                    f'Matrícula: {funcionario["matricula"]}'
                ),
                text_color="gray"
            )

            dados.grid(
                row=1,
                column=0,
                sticky="w",
                padx=15,
                pady=(0, 12)
            )

            # Status
            status_texto = (
                "Ativo"
                if funcionario["ativo"] == 1
                else "Inativo"
            )

            status = ctk.CTkLabel(
                card,
                text=status_texto,
                width=70,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            )

            status.grid(
                row=0,
                column=1,
                rowspan=2,
                padx=10
            )

            # Botão editar
            botao_editar = ctk.CTkButton(
                card,
                text="Editar",
                width=80,
                fg_color=COR_PRINCIPAL,
                hover_color=COR_HOVER,
                command=lambda f=funcionario: self.editar_funcionario(f)
            )

            botao_editar.grid(
                row=0,
                column=2,
                rowspan=2,
                padx=5
            )

            # Botão ativar/desativar
            if funcionario["ativo"] == 1:

                texto_status = "Desativar"

            else:

                texto_status = "Ativar"

            botao_status = ctk.CTkButton(
                card,
                text=texto_status,
                width=90,
                fg_color=COR_INATIVO,
                hover_color="#4B5563",
                command=lambda f=funcionario: self.alternar_status(f)
            )

            botao_status.grid(
                row=0,
                column=3,
                rowspan=2,
                padx=(5, 15)
            )

    # ========================================================
    # EDITAR
    # ========================================================

    def editar_funcionario(self, funcionario):

        self.funcionario_em_edicao = funcionario["id"]

        self.entry_nome.delete(0, "end")
        self.entry_cargo.delete(0, "end")
        self.entry_matricula.delete(0, "end")

        self.entry_nome.insert(
            0,
            funcionario["nome"]
        )

        self.entry_cargo.insert(
            0,
            funcionario["cargo"]
        )

        self.entry_matricula.insert(
            0,
            funcionario["matricula"]
        )

        self.botao_salvar.configure(
            text="Salvar alterações"
        )

        self.botao_cancelar.pack(
            side="left",
            padx=10
        )

        self.entry_nome.focus()

    # ========================================================
    # CANCELAR EDIÇÃO
    # ========================================================

    def cancelar_edicao(self):

        self.limpar_campos()

    # ========================================================
    # ATIVAR / DESATIVAR
    # ========================================================

    def alternar_status(self, funcionario):

        ativo_atual = funcionario["ativo"]

        novo_status = 0 if ativo_atual == 1 else 1

        if novo_status == 0:

            resposta = messagebox.askyesno(
                "Desativar funcionário",
                f'Deseja desativar {funcionario["nome"]}?'
            )

            if not resposta:
                return

        database.alterar_status_funcionario(
            funcionario["id"],
            novo_status
        )

        self.carregar_funcionarios()

    # ========================================================
    # LIMPAR CAMPOS
    # ========================================================

    def limpar_campos(self):

        self.entry_nome.delete(0, "end")
        self.entry_cargo.delete(0, "end")
        self.entry_matricula.delete(0, "end")

        self.funcionario_em_edicao = None

        self.botao_salvar.configure(
            text="Cadastrar"
        )

        self.botao_cancelar.pack_forget()