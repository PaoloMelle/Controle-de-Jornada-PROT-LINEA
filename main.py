import customtkinter as ctk
import sys
from pathlib import Path
from PIL import Image

import database
from consultas import TelaConsultas
from funcionarios import TelaFuncionarios
from jornada import TelaJornada
from relatorios import TelaRelatorios


# ============================================================
# CONFIGURAÇÕES VISUAIS
# ============================================================

COR_PRINCIPAL = "#11BAA9"
COR_HOVER = "#0E9E90"

ctk.set_appearance_mode("System")


# ============================================================
# CAMINHOS DOS ARQUIVOS
# ============================================================

def obter_pasta_recursos():
    """
    Retorna a pasta onde estão os arquivos internos do sistema.

    No PyCharm:
    utiliza a pasta do projeto.

    No executável criado pelo PyInstaller:
    utiliza a pasta temporária interna criada pelo PyInstaller.
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent


PASTA_RECURSOS = obter_pasta_recursos()

PASTA_ASSETS = PASTA_RECURSOS / "assets"

CAMINHO_BRASAO_ICO = PASTA_ASSETS / "brasao.ico"
CAMINHO_LOGO = PASTA_ASSETS / "logo.png"


# ============================================================
# JANELA PRINCIPAL
# ============================================================

class SistemaControleJornada(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # CONFIGURAÇÃO DA JANELA
        # ----------------------------------------------------

        self.title(
            "PROT LINEA - Controle de Jornada"
        )

        self.geometry(
            "1100x700"
        )

        self.minsize(
            950,
            620
        )

        # ----------------------------------------------------
        # ÍCONE DA JANELA
        # ----------------------------------------------------

        if CAMINHO_BRASAO_ICO.exists():

            self.after(
                200,
                lambda: self.iconbitmap(
                    str(CAMINHO_BRASAO_ICO)
                )
            )

        # ----------------------------------------------------
        # CONFIGURAÇÃO DO GRID PRINCIPAL
        # ----------------------------------------------------

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.criar_menu_lateral()
        self.criar_area_principal()

    # ========================================================
    # MENU LATERAL
    # ========================================================

    def criar_menu_lateral(self):

        self.menu = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0
        )

        self.menu.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.menu.grid_propagate(
            False
        )

        self.menu.grid_rowconfigure(
            10,
            weight=1
        )

        # ----------------------------------------------------
        # LOGO DA EMPRESA
        # ----------------------------------------------------

        if CAMINHO_LOGO.exists():

            imagem_logo = Image.open(
                CAMINHO_LOGO
            )

            self.logo_empresa = ctk.CTkImage(
                light_image=imagem_logo,
                dark_image=imagem_logo,
                size=(170, 70)
            )

            empresa = ctk.CTkLabel(
                self.menu,
                text="",
                image=self.logo_empresa
            )

        else:

            # Caso a imagem não seja encontrada,
            # exibe o nome da empresa como segurança.
            empresa = ctk.CTkLabel(
                self.menu,
                text="PROT LINEA",
                font=ctk.CTkFont(
                    size=27,
                    weight="bold"
                ),
                text_color=COR_PRINCIPAL
            )

        empresa.grid(
            row=0,
            column=0,
            padx=25,
            pady=(25, 3)
        )

        sistema = ctk.CTkLabel(
            self.menu,
            text="Controle de Jornada",
            font=ctk.CTkFont(
                size=14
            ),
            text_color="gray"
        )

        sistema.grid(
            row=1,
            column=0,
            padx=25,
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # BOTÕES DO MENU
        # ----------------------------------------------------

        self.botao_inicio = self.criar_botao_menu(
            "Início",
            2,
            self.mostrar_inicio
        )

        self.botao_funcionarios = self.criar_botao_menu(
            "Funcionários",
            3,
            self.mostrar_funcionarios
        )

        self.botao_jornada = self.criar_botao_menu(
            "Registrar Jornada",
            4,
            self.mostrar_jornada
        )

        self.botao_consultas = self.criar_botao_menu(
            "Consultas",
            5,
            self.mostrar_consultas
        )

        self.botao_relatorios = self.criar_botao_menu(
            "Relatórios",
            6,
            self.mostrar_relatorios
        )

        # ----------------------------------------------------
        # RODAPÉ
        # ----------------------------------------------------

        rodape = ctk.CTkLabel(
            self.menu,
            text=(
                "Sistema de Controle\n"
                "Administrativo"
            ),
            font=ctk.CTkFont(
                size=12
            ),
            text_color="gray"
        )

        rodape.grid(
            row=11,
            column=0,
            padx=20,
            pady=25
        )

    # ========================================================
    # CRIAR BOTÃO DO MENU
    # ========================================================

    def criar_botao_menu(
        self,
        texto,
        linha,
        comando
    ):

        botao = ctk.CTkButton(
            self.menu,
            text=texto,
            height=45,
            corner_radius=8,
            fg_color=COR_PRINCIPAL,
            hover_color=COR_HOVER,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=comando
        )

        botao.grid(
            row=linha,
            column=0,
            padx=20,
            pady=7,
            sticky="ew"
        )

        return botao

    # ========================================================
    # ÁREA PRINCIPAL
    # ========================================================

    def criar_area_principal(self):

        self.area_principal = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )

        self.area_principal.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=30,
            pady=25
        )

        self.area_principal.grid_columnconfigure(
            0,
            weight=1
        )

        self.area_principal.grid_rowconfigure(
            0,
            weight=1
        )

        self.mostrar_inicio()

    # ========================================================
    # LIMPAR ÁREA PRINCIPAL
    # ========================================================

    def limpar_area_principal(self):

        for widget in self.area_principal.winfo_children():

            widget.destroy()

    # ========================================================
    # TELA INICIAL
    # ========================================================

    def mostrar_inicio(self):

        self.limpar_area_principal()

        frame = ctk.CTkFrame(
            self.area_principal,
            fg_color="transparent"
        )

        frame.pack(
            fill="both",
            expand=True
        )

        titulo = ctk.CTkLabel(
            frame,
            text="Painel Inicial",
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
            frame,
            text=(
                "Controle administrativo da jornada "
                "de trabalho da PROT LINEA."
            ),
            font=ctk.CTkFont(
                size=15
            ),
            text_color="gray"
        )

        subtitulo.pack(
            anchor="w",
            pady=(0, 30)
        )

        # ----------------------------------------------------
        # CARD PRINCIPAL
        # ----------------------------------------------------

        card = ctk.CTkFrame(
            frame,
            corner_radius=15
        )

        card.pack(
            fill="x",
            pady=(0, 20)
        )

        card_titulo = ctk.CTkLabel(
            card,
            text="Controle de Jornada",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            ),
            text_color=COR_PRINCIPAL
        )

        card_titulo.pack(
            anchor="w",
            padx=25,
            pady=(25, 8)
        )

        card_texto = ctk.CTkLabel(
            card,
            text=(
                "Utilize o menu lateral para cadastrar funcionários, "
                "registrar os horários da jornada de trabalho, realizar "
                "consultas e gerar relatórios."
            ),
            font=ctk.CTkFont(
                size=15
            ),
            justify="left",
            wraplength=700
        )

        card_texto.pack(
            anchor="w",
            padx=25,
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # INFORMAÇÕES DA EMPRESA
        # ----------------------------------------------------

        informacoes = ctk.CTkFrame(
            frame,
            corner_radius=15
        )

        informacoes.pack(
            fill="x"
        )

        info_titulo = ctk.CTkLabel(
            informacoes,
            text="PROT LINEA",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        info_titulo.pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        info_texto = ctk.CTkLabel(
            informacoes,
            text=(
                "Sistema desenvolvido para auxiliar no registro "
                "e acompanhamento da jornada dos colaboradores."
            ),
            font=ctk.CTkFont(
                size=14
            ),
            text_color="gray"
        )

        info_texto.pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    # ========================================================
    # FUNCIONÁRIOS
    # ========================================================

    def mostrar_funcionarios(self):

        self.limpar_area_principal()

        TelaFuncionarios(
            self.area_principal
        )

    # ========================================================
    # REGISTRAR JORNADA
    # ========================================================

    def mostrar_jornada(self):

        self.limpar_area_principal()

        TelaJornada(
            self.area_principal
        )

    # ========================================================
    # CONSULTAS
    # ========================================================

    def mostrar_consultas(self):

        self.limpar_area_principal()

        TelaConsultas(
            self.area_principal
        )

    # ========================================================
    # RELATÓRIOS
    # ========================================================

    def mostrar_relatorios(self):

        self.limpar_area_principal()

        TelaRelatorios(
            self.area_principal
        )


# ============================================================
# INICIALIZAÇÃO DO SISTEMA
# ============================================================

if __name__ == "__main__":

    database.criar_banco()

    app = SistemaControleJornada()

    app.mainloop()