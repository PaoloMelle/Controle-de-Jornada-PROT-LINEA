import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

import database


# ============================================================
# CORES DO SISTEMA
# ============================================================

COR_PRINCIPAL = "#11BAA9"
COR_HOVER = "#0E9E90"
COR_SECUNDARIA = "#6B7280"


class TelaRelatorios(ctk.CTkFrame):

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
            text="Relatórios",
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
                "Gere relatórios de jornada em PDF ou Excel "
                "por funcionário e período."
            ),
            font=ctk.CTkFont(size=15),
            text_color="gray"
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 25)
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
            text="Filtros do relatório",
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
        # BOTÕES
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

        botao_pdf = ctk.CTkButton(
            frame_botoes,
            text="Gerar PDF",
            width=130,
            height=42,
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER,
            command=self.gerar_pdf
        )

        botao_pdf.pack(
            side="left"
        )

        botao_excel = ctk.CTkButton(
            frame_botoes,
            text="Gerar Excel",
            width=130,
            height=42,
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER,
            command=self.gerar_excel
        )

        botao_excel.pack(
            side="left",
            padx=10
        )

        botao_limpar = ctk.CTkButton(
            frame_botoes,
            text="Limpar filtros",
            width=130,
            height=42,
            fg_color=COR_SECUNDARIA,
            hover_color="#4B5563",
            command=self.limpar_filtros
        )

        botao_limpar.pack(
            side="left"
        )

        # ----------------------------------------------------
        # INFORMAÇÕES
        # ----------------------------------------------------

        card_info = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        card_info.pack(
            fill="x",
            pady=(0, 20)
        )

        titulo_info = ctk.CTkLabel(
            card_info,
            text="Sobre os relatórios",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        titulo_info.pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        texto_info = ctk.CTkLabel(
            card_info,
            text=(
                "O relatório apresenta funcionário, matrícula, cargo, data, "
                "horários registrados, duração do intervalo e total trabalhado.\n\n"
                "Se nenhum funcionário ou período for selecionado, "
                "serão utilizados todos os registros disponíveis."
            ),
            justify="left",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )

        texto_info.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    # ========================================================
    # FUNCIONÁRIOS
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
    # DATAS
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
    # CÁLCULOS
    # ========================================================

    def calcular_intervalo(self, registro):

        inicio = registro["saida_intervalo"]
        fim = registro["retorno_intervalo"]

        if not inicio or not fim:
            return "--"

        try:

            inicio_dt = datetime.strptime(
                inicio,
                "%H:%M:%S"
            )

            fim_dt = datetime.strptime(
                fim,
                "%H:%M:%S"
            )

            total = int(
                (fim_dt - inicio_dt).total_seconds()
            )

            if total < 0:
                return "--"

            horas = total // 3600
            minutos = (total % 3600) // 60

            return f"{horas:02d}h {minutos:02d}min"

        except ValueError:

            return "--"

    def calcular_total_trabalhado(self, registro):

        entrada = registro["entrada"]
        saida_intervalo = registro["saida_intervalo"]
        retorno_intervalo = registro["retorno_intervalo"]
        saida = registro["saida"]

        if not entrada or not saida:
            return "--"

        try:

            entrada_dt = datetime.strptime(
                entrada,
                "%H:%M:%S"
            )

            saida_dt = datetime.strptime(
                saida,
                "%H:%M:%S"
            )

            total = (
                saida_dt -
                entrada_dt
            ).total_seconds()

            if saida_intervalo and retorno_intervalo:

                saida_intervalo_dt = datetime.strptime(
                    saida_intervalo,
                    "%H:%M:%S"
                )

                retorno_intervalo_dt = datetime.strptime(
                    retorno_intervalo,
                    "%H:%M:%S"
                )

                intervalo = (
                    retorno_intervalo_dt -
                    saida_intervalo_dt
                ).total_seconds()

                total -= intervalo

            if total < 0:
                return "--"

            total = int(total)

            horas = total // 3600
            minutos = (total % 3600) // 60

            return f"{horas:02d}h {minutos:02d}min"

        except ValueError:

            return "--"

    # ========================================================
    # BUSCAR REGISTROS
    # ========================================================

    def obter_registros(self):

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

        if data_inicio_texto and not data_inicio:

            messagebox.showwarning(
                "Data inválida",
                "A data inicial deve estar no formato dd/mm/aaaa."
            )

            return None

        if data_fim_texto and not data_fim:

            messagebox.showwarning(
                "Data inválida",
                "A data final deve estar no formato dd/mm/aaaa."
            )

            return None

        if (
            data_inicio and
            data_fim and
            data_inicio > data_fim
        ):

            messagebox.showwarning(
                "Período inválido",
                "A data inicial não pode ser maior que a data final."
            )

            return None

        registros = database.listar_jornadas(
            data_inicio=data_inicio,
            data_fim=data_fim,
            funcionario_id=self.funcionario_selecionado_id
        )

        if not registros:

            messagebox.showinfo(
                "Nenhum registro",
                "Nenhum registro foi encontrado para os filtros selecionados."
            )

            return None

        return registros

    # ========================================================
    # GERAR PDF
    # ========================================================

    def gerar_pdf(self):

        registros = self.obter_registros()

        if not registros:
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório em PDF",
            defaultextension=".pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ],
            initialfile="relatorio_jornada.pdf"
        )

        if not caminho:
            return

        try:

            documento = SimpleDocTemplate(
                caminho,
                pagesize=landscape(A4),
                rightMargin=25,
                leftMargin=25,
                topMargin=25,
                bottomMargin=25
            )

            estilos = getSampleStyleSheet()

            elementos = []

            titulo = Paragraph(
                "<b>PROT LINEA - Relatório de Controle de Jornada</b>",
                estilos["Title"]
            )

            elementos.append(titulo)

            elementos.append(
                Spacer(1, 15)
            )

            gerado_em = datetime.now().strftime(
                "%d/%m/%Y às %H:%M:%S"
            )

            elementos.append(
                Paragraph(
                    f"Relatório gerado em {gerado_em}",
                    estilos["Normal"]
                )
            )

            elementos.append(
                Spacer(1, 15)
            )

            dados = [
                [
                    "Data",
                    "Funcionário",
                    "Matrícula",
                    "Entrada",
                    "Saída Int.",
                    "Retorno",
                    "Saída",
                    "Intervalo",
                    "Total"
                ]
            ]

            for registro in registros:

                data_formatada = datetime.strptime(
                    registro["data"],
                    "%Y-%m-%d"
                ).strftime(
                    "%d/%m/%Y"
                )

                dados.append(
                    [
                        data_formatada,
                        registro["nome"],
                        registro["matricula"],
                        registro["entrada"] or "--",
                        registro["saida_intervalo"] or "--",
                        registro["retorno_intervalo"] or "--",
                        registro["saida"] or "--",
                        self.calcular_intervalo(registro),
                        self.calcular_total_trabalhado(registro)
                    ]
                )

            tabela = Table(
                dados,
                repeatRows=1,
                colWidths=[
                    65,
                    130,
                    60,
                    65,
                    70,
                    65,
                    65,
                    85,
                    90
                ]
            )

            tabela.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(COR_PRINCIPAL)
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.white
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold"
                        ),
                        (
                            "ALIGN",
                            (0, 0),
                            (-1, -1),
                            "CENTER"
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE"
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            8
                        ),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [
                                colors.white,
                                colors.HexColor("#F3F4F6")
                            ]
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            6
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            6
                        )
                    ]
                )
            )

            elementos.append(tabela)

            documento.build(
                elementos
            )

            messagebox.showinfo(
                "PDF gerado",
                "Relatório em PDF gerado com sucesso."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o PDF.\n\n{erro}"
            )

    # ========================================================
    # GERAR EXCEL
    # ========================================================

    def gerar_excel(self):

        registros = self.obter_registros()

        if not registros:
            return

        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório em Excel",
            defaultextension=".xlsx",
            filetypes=[
                ("Planilha Excel", "*.xlsx")
            ],
            initialfile="relatorio_jornada.xlsx"
        )

        if not caminho:
            return

        try:

            workbook = Workbook()

            planilha = workbook.active

            planilha.title = "Controle de Jornada"

            # ------------------------------------------------
            # TÍTULO
            # ------------------------------------------------

            planilha.merge_cells(
                "A1:J1"
            )

            celula_titulo = planilha["A1"]

            celula_titulo.value = (
                "PROT LINEA - Relatório de Controle de Jornada"
            )

            celula_titulo.font = Font(
                bold=True,
                size=16
            )

            celula_titulo.alignment = Alignment(
                horizontal="center"
            )

            # ------------------------------------------------
            # DATA DE GERAÇÃO
            # ------------------------------------------------

            planilha.merge_cells(
                "A2:J2"
            )

            planilha["A2"] = (
                "Gerado em "
                + datetime.now().strftime(
                    "%d/%m/%Y às %H:%M:%S"
                )
            )

            planilha["A2"].alignment = Alignment(
                horizontal="center"
            )

            # ------------------------------------------------
            # CABEÇALHO
            # ------------------------------------------------

            cabecalhos = [
                "Data",
                "Funcionário",
                "Cargo",
                "Matrícula",
                "Entrada",
                "Saída Intervalo",
                "Retorno",
                "Saída Final",
                "Intervalo",
                "Total Trabalhado"
            ]

            linha_cabecalho = 4

            for coluna, texto in enumerate(
                cabecalhos,
                start=1
            ):

                celula = planilha.cell(
                    row=linha_cabecalho,
                    column=coluna
                )

                celula.value = texto

                celula.font = Font(
                    bold=True
                )

                celula.alignment = Alignment(
                    horizontal="center"
                )

            # ------------------------------------------------
            # DADOS
            # ------------------------------------------------

            linha = 5

            for registro in registros:

                data_formatada = datetime.strptime(
                    registro["data"],
                    "%Y-%m-%d"
                ).strftime(
                    "%d/%m/%Y"
                )

                valores = [
                    data_formatada,
                    registro["nome"],
                    registro["cargo"],
                    registro["matricula"],
                    registro["entrada"] or "--",
                    registro["saida_intervalo"] or "--",
                    registro["retorno_intervalo"] or "--",
                    registro["saida"] or "--",
                    self.calcular_intervalo(registro),
                    self.calcular_total_trabalhado(registro)
                ]

                for coluna, valor in enumerate(
                    valores,
                    start=1
                ):

                    celula = planilha.cell(
                        row=linha,
                        column=coluna
                    )

                    celula.value = valor

                    celula.alignment = Alignment(
                        horizontal="center"
                    )

                linha += 1

            # ------------------------------------------------
            # AJUSTE DE LARGURA DAS COLUNAS
            # ------------------------------------------------

            larguras = {
                "A": 13,
                "B": 25,
                "C": 20,
                "D": 12,
                "E": 12,
                "F": 17,
                "G": 12,
                "H": 12,
                "I": 16,
                "J": 18
            }

            for coluna, largura in larguras.items():

                planilha.column_dimensions[
                    coluna
                ].width = largura

            workbook.save(
                caminho
            )

            messagebox.showinfo(
                "Excel gerado",
                "Relatório em Excel gerado com sucesso."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o Excel.\n\n{erro}"
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