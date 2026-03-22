#!/usr/bin/env python3
"""
KEEPSIDIAN - v0.2.7-alpha
Gerenciador de Senhas + Cofre de Conhecimento
Base: KeePassXC | Inspiração: Obsidian | CFDM AI OS TRIPLEX

CHANGELOG v0.2.7:
- NOVO: Hierarquia por espaços no nome do grupo
- 2 espaços no início = 1 nível de profundidade
- Função build_hierarchy_from_spaces() converte automaticamente
- "  Internet" vira filho de "Senhas" (grupo anterior sem espaços)

CHANGELOG v0.2.6:
- CORREÇÃO: Importar/abrir .kdbx agora lê caminho COMPLETO dos grupos
- Função get_group_path() percorre hierarquia até a raiz
- Tags também são importadas corretamente
- Debug mostra grupo de cada entrada

CHANGELOG v0.2.5:
- CORREÇÃO: Grupos são criados ao importar/salvar .kdbx
- CORREÇÃO: Entradas duplicadas recebem sufixo numérico automático
- Suporte a hierarquia de grupos (Pasta/Subpasta)
- Documentação para Obsidian (docs/)

CHANGELOG v0.2.4:
- CORREÇÃO: "Salvar Como" agora cria novo arquivo corretamente
- CORREÇÃO: Nome do arquivo atualiza no título da aplicação
- Limpa instância .kdbx antiga para forçar novo arquivo

CHANGELOG v0.2.3:
- CORREÇÃO: Salvar Como agora pede senha se necessário
- CORREÇÃO: Tags são atualizadas ao salvar
- Confirmação visual ao salvar arquivo
- Debug melhorado no salvamento

CHANGELOG v0.2.2:
- Menu de contexto para ENTRADAS (botão direito)
  - Editar, clonar, copiar usuário/senha/URL, mover para grupo, excluir
- Arrastar e soltar grupos na árvore
- Mover entradas para qualquer grupo via menu
- Clonar entradas

CHANGELOG v0.2.1:
- Menu de contexto completo para GRUPOS (botão direito)
  - Novo grupo, subgrupo, renomear, clonar, mover, excluir
- Tags salvam/carregam corretamente em .kdbx
- Importação CSV preserva grupos originais
- Árvore de grupos dinâmica baseada nas entradas
- Filtro por grupo na tabela de entradas
- Diálogo de entrada com botões min/max/fechar
- Enter salva em qualquer campo do formulário
- Mensagens de erro mais específicas

CHANGELOG v0.2.0:
- SUPORTE NATIVO A .KDBX (criar, abrir, salvar)
- Diálogo de desbloqueio com suporte a arquivo-chave
- Novo banco de dados já salva como .kdbx
- Compatibilidade total com KeePassXC

CHANGELOG v0.1.9:
- Dashboard de Status e Monitoramento (Ctrl+D)
- Monitor de Sistema (CPU, Memória, Disco)
- Status dos provedores de IA em tempo real
- Estatísticas do Vault (entradas, tags, backlinks)
- Log de atividades com auto-refresh

CHANGELOG v0.1.8:
- Editor Markdown com Preview em tempo real
- Suporte a backlinks [[nota]]
- Sistema de Tags
- Graph View (mapa de conexões)
- Integração Multi-IA (Ollama, Groq, OpenAI, Anthropic)
"""

import sys
import os
import json
import random
import string
import hashlib
import math
import re
from datetime import datetime
from pathlib import Path

# Verificar PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
        QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter, QFrame,
        QMenuBar, QMenu, QAction, QToolBar, QStatusBar, QTabWidget,
        QDialog, QDialogButtonBox, QFormLayout, QComboBox, QCheckBox,
        QMessageBox, QInputDialog, QHeaderView, QAbstractItemView,
        QPlainTextEdit, QGroupBox, QStackedWidget, QFileDialog,
        QSpinBox, QSlider, QProgressBar, QListWidget, QListWidgetItem,
        QRadioButton, QButtonGroup, QSizePolicy, QTextBrowser,
        QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem,
        QDockWidget
    )
    from PyQt5.QtCore import Qt, QSize, QTimer, QPointF
    from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QClipboard, QPen, QBrush, QPainter
except ImportError:
    print("ERRO: PyQt5 não instalado!")
    print("Execute: sudo apt-get install python3-pyqt5")
    sys.exit(1)

# Versão
VERSION = "0.2.7-alpha"
APP_NAME = "Keepsidian"

# Verificar markdown
MARKDOWN_AVAILABLE = False
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    pass

# Verificar requests para IA
REQUESTS_AVAILABLE = False
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    pass

# Verificar pykeepass para arquivos .kdbx
PYKEEPASS_AVAILABLE = False
try:
    from pykeepass import PyKeePass, create_database
    PYKEEPASS_AVAILABLE = True
except ImportError:
    pass

# Estilos baseados no KeePassXC
KEEPASS_STYLE = """
QMainWindow, QDialog {
    background-color: #f5f5f5;
    color: #333333;
}
QMenuBar {
    background-color: #ffffff;
    color: #333333;
    border-bottom: 1px solid #e0e0e0;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #e8e8e8;
}
QMenu {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
}
QMenu::item:selected {
    background-color: #0078d4;
    color: white;
}
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    spacing: 2px;
    padding: 3px;
}
QToolButton {
    background-color: transparent;
    color: #333333;
    border: 1px solid transparent;
    padding: 4px 8px;
    border-radius: 3px;
}
QToolButton:hover {
    background-color: #e8e8e8;
    border: 1px solid #cccccc;
}
QToolButton:pressed {
    background-color: #d0d0d0;
}
QStatusBar {
    background-color: #f0f0f0;
    color: #666666;
    border-top: 1px solid #e0e0e0;
}
QTreeWidget, QTableWidget, QListWidget {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    selection-background-color: #0078d4;
    selection-color: white;
    alternate-background-color: #fafafa;
}
QTreeWidget::item:hover, QTableWidget::item:hover {
    background-color: #e8f4fd;
}
QHeaderView::section {
    background-color: #f5f5f5;
    color: #333333;
    border: none;
    border-right: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
    padding: 5px;
    font-weight: bold;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px 8px;
}
QLineEdit:focus, QSpinBox:focus {
    border-color: #0078d4;
}
QPushButton {
    background-color: #f5f5f5;
    color: #333333;
    border: 1px solid #c0c0c0;
    padding: 6px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #e3f2fd;
    border: 1px solid #90caf9;
}
QPushButton:pressed {
    background-color: #bbdefb;
    border: 1px solid #64b5f6;
}
QPushButton#primaryBtn {
    background-color: #4a9f4d;
    color: white;
    border: 1px solid #3d8b40;
}
QPushButton#primaryBtn:hover {
    background-color: #5cb85c;
    border: 1px solid #4cae4c;
}
QPushButton#primaryBtn:pressed {
    background-color: #398439;
    border: 1px solid #255625;
}
QPushButton#dangerBtn {
    background-color: #d9534f;
    color: white;
    border: 1px solid #c9302c;
}
QPushButton#dangerBtn:hover {
    background-color: #c9302c;
    border: 1px solid #ac2925;
}
QPushButton#dangerBtn:pressed {
    background-color: #ac2925;
    border: 1px solid #761c19;
}
QSplitter::handle {
    background-color: #e0e0e0;
}
QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #f0f0f0;
    color: #666666;
    padding: 8px 16px;
    border: 1px solid #cccccc;
    border-bottom: none;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #333333;
    border-bottom: 1px solid #ffffff;
}
QGroupBox {
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    background-color: #f5f5f5;
}
QLabel {
    color: #333333;
}
QSlider::groove:horizontal {
    background: #e0e0e0;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #4a9f4d;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QProgressBar {
    background-color: #e0e0e0;
    border-radius: 3px;
    text-align: center;
    border: none;
}
QProgressBar::chunk {
    background-color: #4a9f4d;
    border-radius: 3px;
}
QCheckBox {
    color: #333333;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QCheckBox::indicator:unchecked {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background-color: #4a9f4d;
    border: 1px solid #4a9f4d;
    border-radius: 2px;
}
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 6px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #aaaaaa;
}
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
}
"""

# Ícones do KeePassXC (simplificados em texto)
ICONS = {
    "folder": "📁",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓",
    "add": "➕",
    "edit": "✏️",
    "delete": "🗑️",
    "search": "🔍",
    "settings": "⚙️",
    "password": "🔐",
    "note": "📝",
    "card": "💳",
    "ssh": "🔑",
    "save": "💾",
    "open": "📂",
    "new": "🆕",
    "copy": "📋",
    "generate": "🎲",
    "import": "📥",
    "export": "📤",
    "help": "❓",
    "about": "ℹ️",
}


# ==================== CLASSES DE IA ====================

class AIProvider:
    """Classe base para provedores de IA"""

    def __init__(self, name, api_key=None, base_url=None):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.available = False

    def query(self, prompt, model=None):
        raise NotImplementedError

    def get_status(self):
        return "✅ Online" if self.available else "❌ Offline"


class OllamaProvider(AIProvider):
    """Provedor Ollama (Local)"""

    def __init__(self):
        super().__init__("Ollama", base_url="http://localhost:11434")
        self.models = []
        self.check_availability()

    def check_availability(self):
        if not REQUESTS_AVAILABLE:
            self.available = False
            return
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self.available = r.status_code == 200
            if self.available:
                self.models = [m['name'] for m in r.json().get('models', [])]
        except:
            self.available = False
            self.models = []

    def query(self, prompt, model=None):
        if not self.available or not REQUESTS_AVAILABLE:
            return "❌ Ollama não disponível. Verifique se está rodando em localhost:11434"
        try:
            model = model or (self.models[0] if self.models else "llama3.2")
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=120
            )
            return r.json().get('response', 'Sem resposta')
        except Exception as e:
            return f"❌ Erro Ollama: {e}"


class GroqProvider(AIProvider):
    """Provedor Groq (Cloud - Ultra Rápido)"""

    def __init__(self, api_key=None):
        super().__init__("Groq", api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self.available = bool(api_key) and REQUESTS_AVAILABLE

    def query(self, prompt, model="llama-3.3-70b-versatile"):
        if not self.available:
            return "❌ Groq não configurado. Adicione sua API Key nas configurações."
        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048
                },
                timeout=30
            )
            return r.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ Erro Groq: {e}"


class OpenAIProvider(AIProvider):
    """Provedor OpenAI (ChatGPT)"""

    def __init__(self, api_key=None):
        super().__init__("OpenAI", api_key=api_key, base_url="https://api.openai.com/v1")
        self.available = bool(api_key) and REQUESTS_AVAILABLE

    def query(self, prompt, model="gpt-4o-mini"):
        if not self.available:
            return "❌ OpenAI não configurado. Adicione sua API Key nas configurações."
        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048
                },
                timeout=60
            )
            return r.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ Erro OpenAI: {e}"


class AnthropicProvider(AIProvider):
    """Provedor Anthropic (Claude)"""

    def __init__(self, api_key=None):
        super().__init__("Anthropic", api_key=api_key, base_url="https://api.anthropic.com/v1")
        self.available = bool(api_key) and REQUESTS_AVAILABLE

    def query(self, prompt, model="claude-3-5-sonnet-20241022"):
        if not self.available:
            return "❌ Anthropic não configurado. Adicione sua API Key nas configurações."
        try:
            r = requests.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            return r.json()['content'][0]['text']
        except Exception as e:
            return f"❌ Erro Anthropic: {e}"


class AIManager:
    """Gerenciador central de múltiplas IAs"""

    def __init__(self):
        self.providers = {}
        self.config_path = Path.home() / ".keepsidian" / "ai_config.json"
        self.load_providers()

    def load_providers(self):
        """Carrega configurações e inicializa provedores"""
        config = self._load_config()

        self.providers = {
            "ollama": OllamaProvider(),
            "groq": GroqProvider(config.get("groq_api_key")),
            "openai": OpenAIProvider(config.get("openai_api_key")),
            "anthropic": AnthropicProvider(config.get("anthropic_api_key")),
        }

    def _load_config(self):
        """Carrega configurações do arquivo"""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text())
            except:
                pass
        return {}

    def save_config(self, config):
        """Salva configurações"""
        self.config_path.parent.mkdir(exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2))
        self.load_providers()

    def get_available_providers(self):
        """Retorna provedores disponíveis"""
        return {k: v for k, v in self.providers.items() if v.available}

    def query(self, prompt, provider_name="ollama", model=None):
        """Consulta um provedor específico"""
        if provider_name in self.providers:
            return self.providers[provider_name].query(prompt, model)
        return "❌ Provedor não encontrado"

    def query_all(self, prompt):
        """Consulta todos os provedores disponíveis (comparativo)"""
        results = {}
        for name, provider in self.providers.items():
            if provider.available:
                results[name] = provider.query(prompt)
        return results

    def get_status_summary(self):
        """Retorna resumo do status de todos os provedores"""
        summary = []
        for name, provider in self.providers.items():
            status = "✅" if provider.available else "❌"
            summary.append(f"{status} {name.upper()}")
        return " | ".join(summary)


# ==================== WIDGETS ====================

class MarkdownEditor(QWidget):
    """Editor Markdown com preview em tempo real estilo Obsidian"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(
            "Escreva em Markdown...\n\n"
            "# Título\n"
            "## Subtítulo\n"
            "- Lista\n"
            "**negrito** *itálico*\n"
            "[[link para outra nota]]\n"
            "`código`"
        )
        self.editor.textChanged.connect(self.update_preview)
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.6;
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 10px;
            }
        """)
        splitter.addWidget(self.editor)

        # Preview
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.preview.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                padding: 10px;
                background-color: #fafafa;
                border: 1px solid #cccccc;
            }
        """)
        splitter.addWidget(self.preview)

        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

    def update_preview(self):
        text = self.editor.toPlainText()

        if MARKDOWN_AVAILABLE:
            try:
                html = markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br'])
            except:
                html = self._basic_markdown(text)
        else:
            html = self._basic_markdown(text)

        # Estilizar preview
        styled_html = f"""
        <style>
            body {{ color: #333; font-family: 'Segoe UI', Arial, sans-serif; }}
            h1 {{ color: #0078d4; border-bottom: 2px solid #0078d4; padding-bottom: 5px; }}
            h2 {{ color: #4a9f4d; }}
            h3 {{ color: #666; }}
            a {{ color: #e94560; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', monospace; }}
            pre {{ background: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            blockquote {{ border-left: 4px solid #0078d4; padding-left: 15px; color: #666; margin: 10px 0; }}
            ul, ol {{ padding-left: 25px; }}
            li {{ margin: 5px 0; }}
            .backlink {{ background: #e8f4fd; padding: 2px 8px; border-radius: 10px; color: #0078d4; }}
        </style>
        {html}
        """
        self.preview.setHtml(styled_html)

    def _basic_markdown(self, text):
        """Conversão básica de Markdown para HTML sem biblioteca externa"""
        # Headers
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

        # Bold e Italic
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        # Links internos [[link]] - backlinks estilo Obsidian
        text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#\1" class="backlink">🔗 \1</a>', text)

        # Links externos [texto](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

        # Code inline
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        # Code blocks
        text = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)

        # Blockquotes
        text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

        # Lists
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', text, flags=re.DOTALL)

        # Horizontal rule
        text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)

        # Line breaks
        text = text.replace('\n\n', '</p><p>')
        text = f'<p>{text}</p>'

        return text

    def get_text(self):
        return self.editor.toPlainText()

    def set_text(self, text):
        self.editor.setPlainText(text)
        self.update_preview()

    def get_backlinks(self):
        """Extrai backlinks [[link]] do texto"""
        text = self.editor.toPlainText()
        return re.findall(r'\[\[([^\]]+)\]\]', text)


class GraphView(QGraphicsView):
    """Visualização gráfica das conexões entre entradas (estilo Obsidian)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#f5f5f5")))
        self.nodes = {}
        self.edges = []

    def build_graph(self, entries):
        """Constrói o grafo a partir das entradas e seus backlinks"""
        self.scene.clear()
        self.nodes = {}
        self.edges = []

        if not entries:
            # Mostrar mensagem se não há entradas
            text = self.scene.addText("Nenhuma entrada para visualizar")
            text.setDefaultTextColor(QColor("#666"))
            return

        # Calcular posições em círculo
        num_entries = len(entries)
        angle_step = 360 / max(num_entries, 1)
        radius = min(200, 50 + num_entries * 15)
        center_x, center_y = 300, 300

        # Criar nós para cada entrada
        for i, entry in enumerate(entries):
            angle = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # Cor baseada no tipo
            entry_type = entry.get("type", "")
            if "Senha" in entry_type:
                color = QColor("#e94560")  # Vermelho
            elif "Nota" in entry_type:
                color = QColor("#0078d4")  # Azul
            elif "Cartão" in entry_type:
                color = QColor("#f59e0b")  # Amarelo
            else:
                color = QColor("#4ade80")  # Verde

            # Criar nó (círculo)
            node_size = 30
            node = self.scene.addEllipse(
                x - node_size/2, y - node_size/2,
                node_size, node_size,
                QPen(color, 2),
                QBrush(color.lighter(150))
            )
            node.setToolTip(f"{entry.get('title', '')}\n{entry.get('type', '')}")

            # Texto do nó (título abreviado)
            title = entry.get("title", "")[:12]
            if len(entry.get("title", "")) > 12:
                title += "..."
            text = self.scene.addText(title)
            text.setDefaultTextColor(QColor("#333"))
            text.setPos(x - text.boundingRect().width()/2, y + node_size/2 + 5)

            self.nodes[entry.get("title", "")] = {
                "x": x, "y": y,
                "node": node,
                "entry": entry
            }

        # Criar conexões baseadas em backlinks
        for entry in entries:
            title = entry.get("title", "")
            backlinks = entry.get("backlinks", [])

            # Se backlinks está armazenado como string, converter
            if isinstance(backlinks, str):
                backlinks = re.findall(r'\[\[([^\]]+)\]\]', entry.get("notes", ""))

            for link in backlinks:
                # Buscar entrada que corresponde ao link
                for other_title in self.nodes:
                    if link.lower() in other_title.lower() or other_title.lower() in link.lower():
                        self._add_edge(title, other_title)
                        break

        # Ajustar viewport para mostrar todo o grafo
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50))
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def _add_edge(self, from_title, to_title):
        """Adiciona uma aresta entre dois nós"""
        if from_title == to_title:
            return
        if from_title not in self.nodes or to_title not in self.nodes:
            return

        from_node = self.nodes[from_title]
        to_node = self.nodes[to_title]

        # Evitar duplicatas
        edge_key = tuple(sorted([from_title, to_title]))
        if edge_key in [(e[0], e[1]) for e in self.edges]:
            return

        # Criar linha
        line = self.scene.addLine(
            from_node["x"], from_node["y"],
            to_node["x"], to_node["y"],
            QPen(QColor("#0f3460"), 2, Qt.DashLine)
        )
        line.setZValue(-1)  # Colocar atrás dos nós

        self.edges.append((from_title, to_title, line))

    def wheelEvent(self, event):
        """Zoom com scroll do mouse"""
        factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1/factor, 1/factor)


class GraphDialog(QDialog):
    """Diálogo para exibir o Graph View em tela cheia"""

    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self.entries = entries
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("🕸️ Graph View - Mapa de Conexões")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        info_label = QLabel("🕸️ Visualização das conexões entre entradas (backlinks)")
        info_label.setStyleSheet("color: #666;")
        toolbar.addWidget(info_label)

        toolbar.addStretch()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.refresh_graph)
        toolbar.addWidget(refresh_btn)

        fit_btn = QPushButton("📐 Ajustar")
        fit_btn.clicked.connect(self.fit_view)
        toolbar.addWidget(fit_btn)

        layout.addLayout(toolbar)

        # Graph View
        self.graph_view = GraphView()
        self.graph_view.build_graph(self.entries)
        layout.addWidget(self.graph_view)

        # Legenda
        legend = QHBoxLayout()
        legend.addWidget(QLabel("Legenda:"))
        legend.addWidget(QLabel("🔴 Senha"))
        legend.addWidget(QLabel("🔵 Nota"))
        legend.addWidget(QLabel("🟡 Cartão"))
        legend.addWidget(QLabel("🟢 Outro"))
        legend.addWidget(QLabel("--- Conexão (backlink)"))
        legend.addStretch()
        layout.addLayout(legend)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def refresh_graph(self):
        self.graph_view.build_graph(self.entries)

    def fit_view(self):
        self.graph_view.fitInView(self.graph_view.scene.sceneRect(), Qt.KeepAspectRatio)


class AIQueryDialog(QDialog):
    """Diálogo para consultas Multi-IA"""

    def __init__(self, ai_manager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("🤖 Consulta Multi-IA - Keepsidian")
        self.setMinimumSize(750, 550)

        layout = QVBoxLayout(self)

        # Header com status
        header = QHBoxLayout()
        header.addWidget(QLabel("<h3>🤖 Consulta Inteligente</h3>"))
        header.addStretch()

        self.status_label = QLabel(self.ai_manager.get_status_summary())
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        header.addWidget(self.status_label)

        layout.addLayout(header)

        # Seleção de provedor
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Provedor:"))

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("🌐 Todos (Comparar)", "all")
        for name, provider in self.ai_manager.providers.items():
            status = "✅" if provider.available else "❌"
            self.provider_combo.addItem(f"{status} {name.upper()}", name)
        self.provider_combo.setMinimumWidth(200)
        provider_layout.addWidget(self.provider_combo)

        provider_layout.addStretch()

        config_btn = QPushButton("⚙️ Configurar APIs")
        config_btn.clicked.connect(self.show_config)
        provider_layout.addWidget(config_btn)

        layout.addLayout(provider_layout)

        # Área de prompt
        layout.addWidget(QLabel("📝 Prompt:"))
        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setMaximumHeight(120)
        self.prompt_edit.setPlaceholderText(
            "Digite sua pergunta para a IA...\n\n"
            "Exemplos:\n"
            "• Gere uma senha segura de 20 caracteres\n"
            "• Explique o que é autenticação 2FA\n"
            "• Crie uma nota sobre segurança de senhas"
        )
        layout.addWidget(self.prompt_edit)

        # Botões de ação
        action_layout = QHBoxLayout()

        send_btn = QPushButton("🚀 Enviar")
        send_btn.setObjectName("primaryBtn")
        send_btn.clicked.connect(self.send_query)
        action_layout.addWidget(send_btn)

        clear_btn = QPushButton("🗑️ Limpar")
        clear_btn.clicked.connect(self.clear_all)
        action_layout.addWidget(clear_btn)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Área de resposta
        layout.addWidget(QLabel("💬 Resposta:"))
        self.result_text = QTextBrowser()
        self.result_text.setOpenExternalLinks(True)
        self.result_text.setPlaceholderText("A resposta aparecerá aqui...")
        layout.addWidget(self.result_text)

        # Botões inferiores
        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Copiar Resposta")
        copy_btn.clicked.connect(self.copy_result)
        btn_layout.addWidget(copy_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def send_query(self):
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Aviso", "Digite um prompt primeiro!")
            return

        self.result_text.setHtml("<p style='color:#666;'>⏳ Processando consulta...</p>")
        QApplication.processEvents()

        provider = self.provider_combo.currentData()

        try:
            if provider == "all":
                results = self.ai_manager.query_all(prompt)
                if not results:
                    self.result_text.setHtml(
                        "<p style='color:#e94560;'>❌ Nenhum provedor disponível!</p>"
                        "<p>Configure suas API Keys em ⚙️ Configurar APIs</p>"
                    )
                    return

                html = "<h2>📊 Comparativo de Respostas</h2>"
                for name, response in results.items():
                    html += f"""
                    <div style='border:1px solid #ccc; padding:15px; margin:10px 0; border-radius:8px; background:#fafafa;'>
                        <h3 style='color:#0078d4; margin-top:0;'>🤖 {name.upper()}</h3>
                        <p style='white-space:pre-wrap;'>{response}</p>
                    </div>
                    """
                self.result_text.setHtml(html)
            else:
                result = self.ai_manager.query(prompt, provider)
                self.result_text.setHtml(
                    f"<h3 style='color:#0078d4;'>🤖 {provider.upper()}</h3>"
                    f"<p style='white-space:pre-wrap;'>{result}</p>"
                )
        except Exception as e:
            self.result_text.setHtml(f"<p style='color:#e94560;'>❌ Erro: {e}</p>")

    def copy_result(self):
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copiado", "Resposta copiada para a área de transferência!")

    def clear_all(self):
        self.prompt_edit.clear()
        self.result_text.clear()

    def show_config(self):
        dialog = AIConfigDialog(self.ai_manager, self)
        if dialog.exec_():
            # Atualizar status após configuração
            self.status_label.setText(self.ai_manager.get_status_summary())
            # Recarregar combo
            current = self.provider_combo.currentData()
            self.provider_combo.clear()
            self.provider_combo.addItem("🌐 Todos (Comparar)", "all")
            for name, provider in self.ai_manager.providers.items():
                status = "✅" if provider.available else "❌"
                self.provider_combo.addItem(f"{status} {name.upper()}", name)


class AIConfigDialog(QDialog):
    """Diálogo para configuração das APIs de IA"""

    def __init__(self, ai_manager, parent=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.setWindowTitle("⚙️ Configurar Provedores de IA")
        self.setMinimumWidth(550)

        layout = QVBoxLayout(self)

        # Título
        layout.addWidget(QLabel("<h3>🔑 Configure suas API Keys</h3>"))
        layout.addWidget(QLabel("As chaves são armazenadas localmente em ~/.keepsidian/"))

        layout.addSpacing(10)

        # Formulário
        form = QFormLayout()

        # Ollama (local)
        ollama_layout = QHBoxLayout()
        self.ollama_status = QLabel("⏳ Verificando...")
        ollama_layout.addWidget(self.ollama_status)
        ollama_layout.addStretch()
        form.addRow("🦙 Ollama (Local):", ollama_layout)

        # Groq
        self.groq_edit = QLineEdit()
        self.groq_edit.setEchoMode(QLineEdit.Password)
        self.groq_edit.setPlaceholderText("gsk_...")
        form.addRow("⚡ Groq API Key:", self.groq_edit)

        # OpenAI
        self.openai_edit = QLineEdit()
        self.openai_edit.setEchoMode(QLineEdit.Password)
        self.openai_edit.setPlaceholderText("sk-...")
        form.addRow("🟢 OpenAI API Key:", self.openai_edit)

        # Anthropic
        self.anthropic_edit = QLineEdit()
        self.anthropic_edit.setEchoMode(QLineEdit.Password)
        self.anthropic_edit.setPlaceholderText("sk-ant-...")
        form.addRow("🟣 Anthropic API Key:", self.anthropic_edit)

        layout.addLayout(form)

        # Info
        info = QLabel(
            "💡 <b>Dicas:</b><br>"
            "• Ollama: Detectado automaticamente em localhost:11434<br>"
            "• Groq: Obtenha em console.groq.com (grátis e rápido!)<br>"
            "• OpenAI: Obtenha em platform.openai.com<br>"
            "• Anthropic: Obtenha em console.anthropic.com"
        )
        info.setStyleSheet("color: #666; font-size: 11px; padding: 10px; background: #f5f5f5; border-radius: 5px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        test_btn = QPushButton("🔍 Testar Conexões")
        test_btn.clicked.connect(self.test_connections)
        btn_layout.addWidget(test_btn)

        save_btn = QPushButton("💾 Salvar")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Verificar Ollama
        self.check_ollama()

    def check_ollama(self):
        """Verifica se Ollama está disponível"""
        ollama = self.ai_manager.providers.get("ollama")
        if ollama:
            ollama.check_availability()
            if ollama.available:
                models = ", ".join(ollama.models[:3]) if ollama.models else "nenhum"
                self.ollama_status.setText(f"✅ Online - Modelos: {models}")
                self.ollama_status.setStyleSheet("color: #4ade80;")
            else:
                self.ollama_status.setText("❌ Offline - Inicie: ollama serve")
                self.ollama_status.setStyleSheet("color: #e94560;")

    def load_config(self):
        """Carrega configurações existentes"""
        config = self.ai_manager._load_config()
        self.groq_edit.setText(config.get("groq_api_key", ""))
        self.openai_edit.setText(config.get("openai_api_key", ""))
        self.anthropic_edit.setText(config.get("anthropic_api_key", ""))

    def save_config(self):
        """Salva configurações"""
        config = {
            "groq_api_key": self.groq_edit.text().strip(),
            "openai_api_key": self.openai_edit.text().strip(),
            "anthropic_api_key": self.anthropic_edit.text().strip()
        }
        self.ai_manager.save_config(config)
        QMessageBox.information(self, "Salvo", "✅ Configurações salvas com sucesso!")
        self.accept()

    def test_connections(self):
        """Testa todas as conexões"""
        self.save_config()  # Salva primeiro para aplicar as keys

        results = []

        for name, provider in self.ai_manager.providers.items():
            if name == "ollama":
                provider.check_availability()
            status = "✅ Online" if provider.available else "❌ Offline"
            results.append(f"{name.upper()}: {status}")

        QMessageBox.information(
            self, "Resultado dos Testes",
            "🔍 Status dos Provedores:\n\n" + "\n".join(results)
        )
        self.check_ollama()


class StatusDashboardDialog(QDialog):
    """Dashboard de Status e Monitoramento - CFDM AI OS TRIPLEX"""

    def __init__(self, parent=None, ai_manager=None, entries=None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.entries = entries or []
        self.update_timer = None
        self.setup_ui()
        self.start_auto_refresh()

    def setup_ui(self):
        self.setWindowTitle("📊 Dashboard de Status - CFDM TRIPLEX")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>📊 CFDM AI OS TRIPLEX - Status Dashboard</h2>"))
        header.addStretch()

        self.last_update = QLabel("Última atualização: --")
        self.last_update.setStyleSheet("color: #666;")
        header.addWidget(self.last_update)

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.clicked.connect(self.refresh_all)
        header.addWidget(refresh_btn)

        layout.addLayout(header)

        # Main content - Split into panels
        content = QHBoxLayout()

        # Left Panel - System & AI Status
        left_panel = QVBoxLayout()

        # System Status
        sys_group = QGroupBox("💻 Sistema")
        sys_layout = QVBoxLayout(sys_group)
        self.sys_info = QLabel("Carregando...")
        self.sys_info.setWordWrap(True)
        sys_layout.addWidget(self.sys_info)
        left_panel.addWidget(sys_group)

        # AI Providers Status
        ai_group = QGroupBox("🤖 Provedores de IA")
        ai_layout = QVBoxLayout(ai_group)
        self.ai_status_list = QListWidget()
        self.ai_status_list.setMaximumHeight(150)
        ai_layout.addWidget(self.ai_status_list)
        left_panel.addWidget(ai_group)

        # App Statistics
        stats_group = QGroupBox("📈 Estatísticas do Vault")
        stats_layout = QVBoxLayout(stats_group)
        self.stats_info = QLabel("Carregando...")
        self.stats_info.setWordWrap(True)
        stats_layout.addWidget(self.stats_info)
        left_panel.addWidget(stats_group)

        content.addLayout(left_panel)

        # Right Panel - Activity Monitor
        right_panel = QVBoxLayout()

        # Activity Table
        activity_group = QGroupBox("📋 Monitor de Atividades")
        activity_layout = QVBoxLayout(activity_group)

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Hora", "Tipo", "Ação", "Status"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setAlternatingRowColors(True)
        activity_layout.addWidget(self.activity_table)

        right_panel.addWidget(activity_group)

        # Quick Actions
        actions_group = QGroupBox("⚡ Ações Rápidas")
        actions_layout = QHBoxLayout(actions_group)

        test_ai_btn = QPushButton("🔍 Testar IAs")
        test_ai_btn.clicked.connect(self.test_all_ai)
        actions_layout.addWidget(test_ai_btn)

        clear_log_btn = QPushButton("🗑️ Limpar Log")
        clear_log_btn.clicked.connect(self.clear_activity_log)
        actions_layout.addWidget(clear_log_btn)

        actions_layout.addStretch()
        right_panel.addWidget(actions_group)

        content.addLayout(right_panel)

        layout.addLayout(content)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)

        layout.addLayout(footer)

        # Initial refresh
        self.refresh_all()

    def start_auto_refresh(self):
        """Inicia atualização automática a cada 5 segundos"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_all)
        self.update_timer.start(5000)

    def refresh_all(self):
        """Atualiza todos os painéis"""
        self.refresh_system_info()
        self.refresh_ai_status()
        self.refresh_stats()
        self.last_update.setText(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

    def refresh_system_info(self):
        """Atualiza informações do sistema"""
        try:
            import platform
            import os

            info_lines = []

            # OS Info
            info_lines.append(f"<b>Sistema:</b> {platform.system()} {platform.release()}")
            info_lines.append(f"<b>Python:</b> {platform.python_version()}")

            # Memory (basic)
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if 'MemTotal' in line:
                            total = int(line.split()[1]) // 1024
                            info_lines.append(f"<b>Memória Total:</b> {total} MB")
                        elif 'MemAvailable' in line:
                            available = int(line.split()[1]) // 1024
                            info_lines.append(f"<b>Memória Disponível:</b> {available} MB")
            except:
                info_lines.append("<b>Memória:</b> Não disponível")

            # CPU Load
            try:
                load = os.getloadavg()
                info_lines.append(f"<b>CPU Load:</b> {load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}")
            except:
                info_lines.append("<b>CPU Load:</b> Não disponível")

            # Disk
            try:
                statvfs = os.statvfs('/')
                total_gb = (statvfs.f_frsize * statvfs.f_blocks) / (1024**3)
                free_gb = (statvfs.f_frsize * statvfs.f_bfree) / (1024**3)
                info_lines.append(f"<b>Disco:</b> {free_gb:.1f} GB livres de {total_gb:.1f} GB")
            except:
                info_lines.append("<b>Disco:</b> Não disponível")

            self.sys_info.setText("<br>".join(info_lines))

        except Exception as e:
            self.sys_info.setText(f"Erro ao obter info do sistema: {str(e)}")

    def refresh_ai_status(self):
        """Atualiza status dos provedores de IA"""
        self.ai_status_list.clear()

        if not self.ai_manager:
            self.ai_status_list.addItem("❓ AI Manager não disponível")
            return

        for name, provider in self.ai_manager.providers.items():
            if name == "ollama":
                provider.check_availability()

            status_icon = "✅" if provider.available else "❌"
            status_text = "Online" if provider.available else "Offline"

            extra_info = ""
            if name == "ollama" and provider.available and hasattr(provider, 'models'):
                model_count = len(provider.models) if provider.models else 0
                extra_info = f" ({model_count} modelos)"

            item = QListWidgetItem(f"{status_icon} {name.upper()}: {status_text}{extra_info}")

            if provider.available:
                item.setForeground(QColor("#4ade80"))
            else:
                item.setForeground(QColor("#e94560"))

            self.ai_status_list.addItem(item)

    def refresh_stats(self):
        """Atualiza estatísticas do vault"""
        try:
            total_entries = len(self.entries)

            # Contagem por tipo
            type_counts = {}
            tag_counts = {}
            backlink_count = 0

            for entry in self.entries:
                # Tipo
                entry_type = entry.get("type", "🔐 Senha")
                type_counts[entry_type] = type_counts.get(entry_type, 0) + 1

                # Tags
                tags = entry.get("tags", "")
                if tags:
                    for tag in tags.split(","):
                        tag = tag.strip()
                        if tag:
                            tag_counts[tag] = tag_counts.get(tag, 0) + 1

                # Backlinks
                notes = entry.get("notes", "")
                backlinks = re.findall(r'\[\[([^\]]+)\]\]', notes)
                backlink_count += len(backlinks)

            info_lines = [
                f"<b>Total de Entradas:</b> {total_entries}",
                "",
                "<b>Por Tipo:</b>"
            ]

            for t, count in type_counts.items():
                info_lines.append(f"  • {t}: {count}")

            info_lines.append("")
            info_lines.append(f"<b>Tags Únicas:</b> {len(tag_counts)}")
            info_lines.append(f"<b>Backlinks:</b> {backlink_count} conexões")

            if tag_counts:
                top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                info_lines.append("")
                info_lines.append("<b>Top Tags:</b>")
                for tag, count in top_tags:
                    info_lines.append(f"  • {tag}: {count}")

            self.stats_info.setText("<br>".join(info_lines))

        except Exception as e:
            self.stats_info.setText(f"Erro ao calcular estatísticas: {str(e)}")

    def test_all_ai(self):
        """Testa todos os provedores de IA"""
        if not self.ai_manager:
            QMessageBox.warning(self, "Aviso", "AI Manager não disponível")
            return

        self.log_activity("🤖 AI", "Iniciando teste de conexões...")

        results = []
        for name, provider in self.ai_manager.providers.items():
            if name == "ollama":
                provider.check_availability()

            status = "✅ Online" if provider.available else "❌ Offline"
            results.append(f"{name.upper()}: {status}")

            self.log_activity("🤖 AI", f"Testando {name.upper()}", status)

        self.refresh_ai_status()
        QMessageBox.information(
            self, "Teste Concluído",
            "🔍 Resultado:\n\n" + "\n".join(results)
        )

    def log_activity(self, activity_type, action, status="⏳"):
        """Adiciona entrada ao log de atividades"""
        row = self.activity_table.rowCount()
        self.activity_table.insertRow(row)

        time_str = datetime.now().strftime("%H:%M:%S")
        self.activity_table.setItem(row, 0, QTableWidgetItem(time_str))
        self.activity_table.setItem(row, 1, QTableWidgetItem(activity_type))
        self.activity_table.setItem(row, 2, QTableWidgetItem(action))
        self.activity_table.setItem(row, 3, QTableWidgetItem(status))

        # Limitar a 100 entradas
        while self.activity_table.rowCount() > 100:
            self.activity_table.removeRow(0)

        self.activity_table.scrollToBottom()

    def clear_activity_log(self):
        """Limpa o log de atividades"""
        self.activity_table.setRowCount(0)
        self.log_activity("📊 Sistema", "Log limpo", "✅")

    def closeEvent(self, event):
        """Para o timer ao fechar"""
        if self.update_timer:
            self.update_timer.stop()
        super().closeEvent(event)


class WelcomeWidget(QWidget):
    """Tela de boas-vindas estilo KeePassXC (Foto 013-014)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Espaçamento superior
        layout.addStretch(2)

        # Logo/Ícone
        logo = QLabel("🔐")
        logo.setStyleSheet("font-size: 72px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Título
        title = QLabel(f"Bem-vindo ao {APP_NAME} {VERSION}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Comece a guardar suas senhas de maneira segura em um banco de dados do Keepsidian.")
        subtitle.setStyleSheet("font-size: 12px; color: #666;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        # Criar Banco de Dados
        create_btn = QPushButton("➕ Criar Banco de Dados")
        create_btn.setMinimumSize(180, 40)
        create_btn.clicked.connect(self.on_create)
        btn_layout.addWidget(create_btn)

        # Abrir Banco de Dados
        open_btn = QPushButton("📂 Abrir Banco de Dados")
        open_btn.setObjectName("primaryBtn")
        open_btn.setMinimumSize(180, 40)
        open_btn.clicked.connect(self.on_open)
        btn_layout.addWidget(open_btn)

        # Importar Arquivo
        import_btn = QPushButton("📥 Importar Arquivo")
        import_btn.setMinimumSize(180, 40)
        import_btn.clicked.connect(self.on_import)
        btn_layout.addWidget(import_btn)

        layout.addLayout(btn_layout)

        # Espaçamento inferior
        layout.addStretch(3)

    def on_create(self):
        if self.parent_window:
            self.parent_window.new_vault()

    def on_open(self):
        if self.parent_window:
            self.parent_window.open_vault()

    def on_import(self):
        if self.parent_window:
            self.parent_window.show_import_wizard()


class PasswordGeneratorDialog(QDialog):
    """Gerador de Senhas estilo KeePassXC (Foto 010)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.generated_password = ""
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Gerador de Senha - Keepsidian")
        self.setMinimumSize(550, 400)

        layout = QVBoxLayout(self)

        # Senha gerada
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Consolas", 14))
        self.password_display.setMinimumHeight(35)
        layout.addWidget(self.password_display)

        # Barra de qualidade
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualidade da senha:"))
        self.quality_label = QLabel("Excelente")
        self.quality_label.setStyleSheet("color: #4a9f4d; font-weight: bold;")
        quality_layout.addWidget(self.quality_label)
        quality_layout.addStretch()
        quality_layout.addWidget(QLabel("Caracteres:"))
        self.chars_label = QLabel("20")
        quality_layout.addWidget(self.chars_label)
        quality_layout.addStretch()
        quality_layout.addWidget(QLabel("Entropia:"))
        self.entropy_label = QLabel("120.62 bit")
        quality_layout.addWidget(self.entropy_label)
        layout.addLayout(quality_layout)

        # Barra de progresso verde
        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setValue(100)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setMaximumHeight(8)
        layout.addWidget(self.strength_bar)

        # Botões de ação (direita)
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        view_btn = QPushButton("👁️")
        view_btn.setMaximumWidth(40)
        view_btn.setToolTip("Mostrar/Ocultar senha")
        view_btn.clicked.connect(self.toggle_view)
        action_layout.addWidget(view_btn)

        regen_btn = QPushButton("🔄")
        regen_btn.setMaximumWidth(40)
        regen_btn.setToolTip("Regenerar")
        regen_btn.clicked.connect(self.generate_password)
        action_layout.addWidget(regen_btn)

        copy_btn = QPushButton("📋")
        copy_btn.setMaximumWidth(40)
        copy_btn.setToolTip("Copiar")
        copy_btn.clicked.connect(self.copy_password)
        action_layout.addWidget(copy_btn)

        layout.addLayout(action_layout)

        layout.addSpacing(10)

        # Tabs: Senha | Frase secreta
        self.tabs = QTabWidget()

        # Tab Senha
        password_tab = QWidget()
        pass_layout = QVBoxLayout(password_tab)

        # Tamanho
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Tamanho:"))
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(20)
        self.length_slider.valueChanged.connect(self.on_length_changed)
        length_layout.addWidget(self.length_slider)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(20)
        self.length_spin.valueChanged.connect(lambda v: self.length_slider.setValue(v))
        length_layout.addWidget(self.length_spin)
        adv_btn = QPushButton("Avançado")
        length_layout.addWidget(adv_btn)
        pass_layout.addLayout(length_layout)

        pass_layout.addSpacing(10)

        # Tipo de Caracteres
        chars_group = QGroupBox("Tipo de Caracteres")
        chars_layout = QHBoxLayout(chars_group)

        self.upper_btn = QPushButton("A-Z")
        self.upper_btn.setCheckable(True)
        self.upper_btn.setChecked(True)
        self.upper_btn.setStyleSheet("QPushButton:checked { background-color: #4a9f4d; color: white; }")
        self.upper_btn.clicked.connect(self.generate_password)
        chars_layout.addWidget(self.upper_btn)

        self.lower_btn = QPushButton("a-z")
        self.lower_btn.setCheckable(True)
        self.lower_btn.setChecked(True)
        self.lower_btn.setStyleSheet("QPushButton:checked { background-color: #4a9f4d; color: white; }")
        self.lower_btn.clicked.connect(self.generate_password)
        chars_layout.addWidget(self.lower_btn)

        self.numbers_btn = QPushButton("0-9")
        self.numbers_btn.setCheckable(True)
        self.numbers_btn.setChecked(True)
        self.numbers_btn.setStyleSheet("QPushButton:checked { background-color: #4a9f4d; color: white; }")
        self.numbers_btn.clicked.connect(self.generate_password)
        chars_layout.addWidget(self.numbers_btn)

        self.symbols_btn = QPushButton("/*+&...")
        self.symbols_btn.setCheckable(True)
        self.symbols_btn.setChecked(True)
        self.symbols_btn.setStyleSheet("QPushButton:checked { background-color: #4a9f4d; color: white; }")
        self.symbols_btn.clicked.connect(self.generate_password)
        chars_layout.addWidget(self.symbols_btn)

        self.ascii_btn = QPushButton("ASCII extendido")
        self.ascii_btn.setCheckable(True)
        self.ascii_btn.clicked.connect(self.generate_password)
        chars_layout.addWidget(self.ascii_btn)

        pass_layout.addWidget(chars_group)

        self.tabs.addTab(password_tab, "Senha")

        # Tab Frase secreta
        phrase_tab = QWidget()
        phrase_layout = QVBoxLayout(phrase_tab)
        phrase_layout.addWidget(QLabel("Gerador de frase secreta (em desenvolvimento)"))
        self.tabs.addTab(phrase_tab, "Frase secreta")

        layout.addWidget(self.tabs)

        layout.addStretch()

        # Botão Fechar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        # Gerar senha inicial
        self.generate_password()

    def on_length_changed(self, value):
        self.length_spin.setValue(value)
        self.generate_password()

    def toggle_view(self):
        if self.password_display.echoMode() == QLineEdit.Password:
            self.password_display.setEchoMode(QLineEdit.Normal)
        else:
            self.password_display.setEchoMode(QLineEdit.Password)

    def generate_password(self):
        chars = ""
        if self.upper_btn.isChecked():
            chars += string.ascii_uppercase
        if self.lower_btn.isChecked():
            chars += string.ascii_lowercase
        if self.numbers_btn.isChecked():
            chars += string.digits
        if self.symbols_btn.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        if self.ascii_btn.isChecked():
            chars += "".join(chr(i) for i in range(128, 256) if chr(i).isprintable())

        if not chars:
            chars = string.ascii_letters + string.digits

        length = self.length_slider.value()
        self.generated_password = ''.join(random.choice(chars) for _ in range(length))
        self.password_display.setText(self.generated_password)
        self.chars_label.setText(str(length))

        # Calcular entropia
        pool_size = len(set(chars))
        entropy = length * math.log2(pool_size) if pool_size > 0 else 0
        self.entropy_label.setText(f"{entropy:.2f} bit")

        # Qualidade
        if entropy < 40:
            self.quality_label.setText("Fraca")
            self.quality_label.setStyleSheet("color: #d9534f; font-weight: bold;")
            self.strength_bar.setValue(25)
        elif entropy < 60:
            self.quality_label.setText("Razoável")
            self.quality_label.setStyleSheet("color: #f0ad4e; font-weight: bold;")
            self.strength_bar.setValue(50)
        elif entropy < 80:
            self.quality_label.setText("Boa")
            self.quality_label.setStyleSheet("color: #5bc0de; font-weight: bold;")
            self.strength_bar.setValue(75)
        else:
            self.quality_label.setText("Excelente")
            self.quality_label.setStyleSheet("color: #4a9f4d; font-weight: bold;")
            self.strength_bar.setValue(100)

    def copy_password(self):
        QApplication.clipboard().setText(self.generated_password)
        QMessageBox.information(self, "Copiado", "Senha copiada para a área de transferência!")

    def get_password(self):
        return self.generated_password


class NewVaultWizard(QDialog):
    """Wizard de criação de banco estilo KeePassXC (Fotos 015-017)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Criar um novo banco de dados Keepsidian...")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout(self)

        # Conteúdo principal com ícone
        content = QHBoxLayout()

        # Ícone grande
        icon_label = QLabel("🔑")
        icon_label.setStyleSheet("font-size: 120px; color: #4a9f4d;")
        icon_label.setAlignment(Qt.AlignTop)
        content.addWidget(icon_label)

        # Formulário
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        self.stack = QStackedWidget()

        # Página 1: Informações gerais
        page1 = QWidget()
        p1_layout = QVBoxLayout(page1)

        p1_layout.addWidget(QLabel("<h2>Informações Gerais Sobre o Banco de Dados</h2>"))
        p1_layout.addWidget(QLabel("Por favor preencha o nome de exibição e uma descrição opcional para o seu novo banco de dados:"))
        p1_layout.addSpacing(20)

        form1 = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setText("Senhas")
        form1.addRow("Nome do banco de dados:", self.name_edit)

        self.desc_edit = QLineEdit()
        form1.addRow("Descrição:", self.desc_edit)
        p1_layout.addLayout(form1)

        p1_layout.addStretch()
        self.stack.addWidget(page1)

        # Página 2: Definições de cifra
        page2 = QWidget()
        p2_layout = QVBoxLayout(page2)

        p2_layout.addWidget(QLabel("<h2>Definições de cifra</h2>"))
        p2_layout.addWidget(QLabel("Aqui você pode ajustar as configurações de criptografia do banco de dados."))
        p2_layout.addSpacing(20)

        form2 = QFormLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["KDBX 4 (recomendado)", "KDBX 3"])
        form2.addRow("Formato de banco de dados:", self.format_combo)
        p2_layout.addLayout(form2)

        p2_layout.addSpacing(10)
        p2_layout.addWidget(QLabel("<b>Configurações de criptografia:</b>"))

        crypto_tabs = QTabWidget()
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora da descriptografia:"))
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(100, 5000)
        self.time_slider.setValue(1000)
        time_layout.addWidget(self.time_slider)
        self.time_label = QLabel("1.0 s")
        time_layout.addWidget(self.time_label)
        self.time_slider.valueChanged.connect(lambda v: self.time_label.setText(f"{v/1000:.1f} s"))
        basic_layout.addLayout(time_layout)

        basic_layout.addWidget(QLabel("Valores mais altos oferecem mais proteção, mas a abertura do banco de dados levará mais tempo."))
        basic_layout.addStretch()

        crypto_tabs.addTab(basic_tab, "Básico")
        crypto_tabs.addTab(QWidget(), "Avançado")
        p2_layout.addWidget(crypto_tabs)

        p2_layout.addStretch()
        self.stack.addWidget(page2)

        # Página 3: Credenciais
        page3 = QWidget()
        p3_layout = QVBoxLayout(page3)

        p3_layout.addWidget(QLabel("<h2>Credenciais do Banco de Dados</h2>"))
        p3_layout.addWidget(QLabel("Um conjunto de credenciais conhecidas apenas por você que protege seu banco de dados."))
        p3_layout.addSpacing(20)

        p3_layout.addWidget(QLabel("<b>Senha</b>"))

        form3 = QFormLayout()

        pass_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.password_edit)
        show_btn = QPushButton("👁️")
        show_btn.setMaximumWidth(40)
        show_btn.clicked.connect(lambda: self.password_edit.setEchoMode(
            QLineEdit.Normal if self.password_edit.echoMode() == QLineEdit.Password else QLineEdit.Password
        ))
        pass_layout.addWidget(show_btn)
        gen_btn = QPushButton("🎲")
        gen_btn.setMaximumWidth(40)
        gen_btn.clicked.connect(self.generate_password)
        pass_layout.addWidget(gen_btn)
        form3.addRow("Insira senha:", pass_layout)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        form3.addRow("Confirmar senha:", self.confirm_edit)
        p3_layout.addLayout(form3)

        p3_layout.addSpacing(15)

        # Proteção adicional - Arquivo-chave
        p3_layout.addWidget(QLabel("<b>Proteção Adicional (Opcional)</b>"))

        keyfile_layout = QHBoxLayout()
        self.keyfile_check = QCheckBox("Usar arquivo-chave:")
        self.keyfile_check.toggled.connect(self.toggle_keyfile)
        keyfile_layout.addWidget(self.keyfile_check)

        self.keyfile_edit = QLineEdit()
        self.keyfile_edit.setPlaceholderText("Selecione um arquivo-chave...")
        self.keyfile_edit.setEnabled(False)
        keyfile_layout.addWidget(self.keyfile_edit)

        self.keyfile_browse_btn = QPushButton("...")
        self.keyfile_browse_btn.setMaximumWidth(40)
        self.keyfile_browse_btn.setEnabled(False)
        self.keyfile_browse_btn.clicked.connect(self.browse_keyfile)
        keyfile_layout.addWidget(self.keyfile_browse_btn)

        self.keyfile_gen_btn = QPushButton("Gerar")
        self.keyfile_gen_btn.setEnabled(False)
        self.keyfile_gen_btn.clicked.connect(self.generate_keyfile)
        keyfile_layout.addWidget(self.keyfile_gen_btn)

        p3_layout.addLayout(keyfile_layout)

        p3_layout.addStretch()
        self.stack.addWidget(page3)

        form_layout.addWidget(self.stack)
        content.addWidget(form_widget)

        layout.addLayout(content)

        # Botões de navegação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.back_btn = QPushButton("Voltar")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        btn_layout.addWidget(self.back_btn)

        self.next_btn = QPushButton("Continuar")
        self.next_btn.setObjectName("primaryBtn")
        self.next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(self.next_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
            self.back_btn.setEnabled(idx - 1 > 0)
            self.next_btn.setText("Continuar")

    def go_next(self):
        idx = self.stack.currentIndex()
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            self.back_btn.setEnabled(True)
            if idx + 1 == self.stack.count() - 1:
                self.next_btn.setText("Concluído")
        else:
            # Validar e aceitar
            if not self.name_edit.text():
                QMessageBox.warning(self, "Erro", "Digite um nome para o banco!")
                self.stack.setCurrentIndex(0)
                return
            if not self.password_edit.text():
                QMessageBox.warning(self, "Erro", "Digite uma senha!")
                return
            if self.password_edit.text() != self.confirm_edit.text():
                QMessageBox.warning(self, "Erro", "As senhas não coincidem!")
                return

            self.result_data = {
                "name": self.name_edit.text(),
                "description": self.desc_edit.text(),
                "password": self.password_edit.text(),
                "keyfile": self.keyfile_edit.text() if self.keyfile_check.isChecked() else None
            }
            self.accept()

    def toggle_keyfile(self, checked):
        self.keyfile_edit.setEnabled(checked)
        self.keyfile_browse_btn.setEnabled(checked)
        self.keyfile_gen_btn.setEnabled(checked)

    def browse_keyfile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo-chave", "",
            "Todos os arquivos (*.*);;Arquivos-chave (*.key *.keyx);;Imagens (*.jpg *.png *.bmp);;Documentos (*.txt *.xml *.doc)"
        )
        if file_path:
            self.keyfile_edit.setText(file_path)

    def generate_keyfile(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar novo arquivo-chave", "chave.key",
            "Arquivos-chave (*.key);;Todos os arquivos (*.*)"
        )
        if file_path:
            try:
                # Gerar arquivo-chave com 64 bytes aleatórios
                import secrets
                key_data = secrets.token_bytes(64)
                with open(file_path, 'wb') as f:
                    f.write(key_data)
                self.keyfile_edit.setText(file_path)
                QMessageBox.information(self, "Sucesso",
                    f"Arquivo-chave gerado:\n{file_path}\n\n"
                    "⚠️ IMPORTANTE: Guarde este arquivo em local seguro!\n"
                    "Sem ele você não conseguirá abrir o banco de dados.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao gerar arquivo-chave:\n{e}")

    def generate_password(self):
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec_():
            self.password_edit.setText(dialog.get_password())
            self.confirm_edit.setText(dialog.get_password())

    def get_data(self):
        return self.result_data


class ImportWizard(QDialog):
    """Assistente de Importação estilo KeePassXC (Fotos 018-020) - com suporte a .kdbx"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.imported_entries = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Assistente de Importação")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # Stack para múltiplas páginas
        self.stack = QStackedWidget()

        # Página 1: Seleção de formato
        page1 = QWidget()
        p1_layout = QVBoxLayout(page1)

        content = QHBoxLayout()

        # Ícone
        icon_label = QLabel("🔑")
        icon_label.setStyleSheet("font-size: 100px; color: #4a9f4d;")
        icon_label.setAlignment(Qt.AlignTop)
        content.addWidget(icon_label)

        # Formulário
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)

        form_layout.addWidget(QLabel("<h2>Importar Arquivo Selecionado</h2>"))

        # Lista de formatos
        self.format_list = QListWidget()
        self.format_list.addItem("🔐 Banco de dados KeePassXC (.kdbx)")
        self.format_list.addItem("📄 Valores separados por vírgulas (.csv)")
        self.format_list.addItem("🔵 Bitwarden (.json)")
        self.format_list.addItem("🅿️ Proton Pass (.json)")
        self.format_list.addItem("① Exportar 1Password (.1pux)")
        self.format_list.setCurrentRow(0)
        form_layout.addWidget(self.format_list)

        # Importar arquivo
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Importar Arquivo:"))
        self.file_edit = QLineEdit()
        file_layout.addWidget(self.file_edit)
        browse_btn = QPushButton("Navegar...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        form_layout.addLayout(file_layout)

        # Importar para
        form_layout.addSpacing(10)
        form_layout.addWidget(QLabel("<b>Importar Para:</b>"))
        self.new_db_radio = QRadioButton("Novo Banco de Dados")
        self.new_db_radio.setChecked(True)
        form_layout.addWidget(self.new_db_radio)

        self.existing_db_radio = QRadioButton("Banco de Dados Atual")
        form_layout.addWidget(self.existing_db_radio)

        content.addWidget(form_widget)
        p1_layout.addLayout(content)
        self.stack.addWidget(page1)

        # Página 2: Senha do arquivo .kdbx
        page2 = QWidget()
        p2_layout = QVBoxLayout(page2)

        p2_content = QHBoxLayout()

        icon2 = QLabel("🔐")
        icon2.setStyleSheet("font-size: 100px; color: #4a9f4d;")
        icon2.setAlignment(Qt.AlignTop)
        p2_content.addWidget(icon2)

        form2_widget = QWidget()
        form2_layout = QVBoxLayout(form2_widget)

        form2_layout.addWidget(QLabel("<h2>Desbloquear Banco de Dados KeePassXC</h2>"))
        form2_layout.addWidget(QLabel("Digite a senha mestra do arquivo .kdbx para importar as entradas:"))
        form2_layout.addSpacing(20)

        self.file_label = QLabel("")
        self.file_label.setStyleSheet("color: #666; font-style: italic;")
        form2_layout.addWidget(self.file_label)

        form2_layout.addSpacing(10)

        pass_form = QFormLayout()
        pass_layout = QHBoxLayout()
        self.kdbx_password = QLineEdit()
        self.kdbx_password.setEchoMode(QLineEdit.Password)
        self.kdbx_password.setPlaceholderText("Senha mestra do arquivo .kdbx")
        pass_layout.addWidget(self.kdbx_password)

        show_btn = QPushButton("👁️")
        show_btn.setMaximumWidth(40)
        show_btn.clicked.connect(lambda: self.kdbx_password.setEchoMode(
            QLineEdit.Normal if self.kdbx_password.echoMode() == QLineEdit.Password else QLineEdit.Password
        ))
        pass_layout.addWidget(show_btn)
        pass_form.addRow("Senha:", pass_layout)

        # Keyfile opcional
        keyfile_layout = QHBoxLayout()
        self.keyfile_edit = QLineEdit()
        self.keyfile_edit.setPlaceholderText("(Opcional)")
        keyfile_layout.addWidget(self.keyfile_edit)
        keyfile_btn = QPushButton("...")
        keyfile_btn.setMaximumWidth(40)
        keyfile_btn.clicked.connect(self.browse_keyfile)
        keyfile_layout.addWidget(keyfile_btn)
        pass_form.addRow("Arquivo-chave:", keyfile_layout)

        form2_layout.addLayout(pass_form)
        form2_layout.addStretch()

        p2_content.addWidget(form2_widget)
        p2_layout.addLayout(p2_content)
        self.stack.addWidget(page2)

        # Página 3: Resultado da importação
        page3 = QWidget()
        p3_layout = QVBoxLayout(page3)

        p3_layout.addWidget(QLabel("<h2>Resultado da Importação</h2>"))

        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 14px;")
        p3_layout.addWidget(self.result_label)

        # Tabela de preview
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["Título", "Usuário", "URL", "Grupo"])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.preview_table.setAlternatingRowColors(True)
        p3_layout.addWidget(self.preview_table)

        self.stack.addWidget(page3)

        layout.addWidget(self.stack)

        # Botões de navegação
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.back_btn = QPushButton("Voltar")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        btn_layout.addWidget(self.back_btn)

        self.next_btn = QPushButton("Continuar")
        self.next_btn.setObjectName("primaryBtn")
        self.next_btn.clicked.connect(self.go_next)
        btn_layout.addWidget(self.next_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def browse_file(self):
        format_idx = self.format_list.currentRow()
        if format_idx == 0:  # .kdbx
            filter_str = "KeePassXC (*.kdbx);;Todos (*.*)"
        elif format_idx == 1:  # CSV
            filter_str = "CSV (*.csv);;Todos (*.*)"
        elif format_idx == 2:  # Bitwarden
            filter_str = "JSON (*.json);;Todos (*.*)"
        else:
            filter_str = "Todos os arquivos (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo de importação", "", filter_str
        )
        if file_path:
            self.file_edit.setText(file_path)

    def browse_keyfile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo-chave", "",
            "Todos os arquivos (*.*);;Arquivos-chave (*.key *.keyx);;Imagens (*.jpg *.png);;Documentos (*.txt *.xml)"
        )
        if file_path:
            self.keyfile_edit.setText(file_path)

    def go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
            self.back_btn.setEnabled(idx - 1 > 0)
            self.next_btn.setText("Continuar")

    def go_next(self):
        idx = self.stack.currentIndex()

        if idx == 0:  # Página de seleção de formato
            if not self.file_edit.text():
                QMessageBox.warning(self, "Erro", "Selecione um arquivo para importar!")
                return

            file_path = self.file_edit.text()
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Erro", "Arquivo não encontrado!")
                return

            format_idx = self.format_list.currentRow()

            if format_idx == 0:  # .kdbx
                if not PYKEEPASS_AVAILABLE:
                    QMessageBox.critical(self, "Erro",
                        "Biblioteca pykeepass não instalada!\n\n"
                        "Execute: pip3 install pykeepass --break-system-packages")
                    return

                self.file_label.setText(f"Arquivo: {file_path}")
                self.stack.setCurrentIndex(1)  # Ir para página de senha
                self.back_btn.setEnabled(True)

            else:  # Outros formatos
                self.import_other_format(file_path, format_idx)

        elif idx == 1:  # Página de senha do .kdbx
            self.import_kdbx()

        elif idx == 2:  # Página de resultado
            self.finish_import()

    def import_kdbx(self):
        """Importa arquivo .kdbx do KeePassXC"""
        file_path = self.file_edit.text()
        password = self.kdbx_password.text()
        keyfile_path = self.keyfile_edit.text().strip() if self.keyfile_edit.text().strip() else None

        if not password and not keyfile_path:
            QMessageBox.warning(self, "Erro", "Digite a senha ou selecione um arquivo-chave!")
            return

        # Verificar se o keyfile existe
        if keyfile_path and not os.path.exists(keyfile_path):
            QMessageBox.warning(self, "Erro", f"Arquivo-chave não encontrado:\n{keyfile_path}")
            return

        try:
            # Debug: mostrar o que está sendo usado
            print(f"[DEBUG] Abrindo: {file_path}")
            print(f"[DEBUG] Senha: {'***' if password else 'VAZIA'}")
            print(f"[DEBUG] Keyfile: {keyfile_path if keyfile_path else 'NENHUM'}")

            # Abrir arquivo .kdbx com pykeepass
            # Se não tem senha mas tem keyfile, passa senha como string vazia
            if not password and keyfile_path:
                kp = PyKeePass(file_path, password='', keyfile=keyfile_path)
            elif password and keyfile_path:
                kp = PyKeePass(file_path, password=password, keyfile=keyfile_path)
            else:
                kp = PyKeePass(file_path, password=password)

            self.imported_entries = []

            def get_group_path(group):
                """Obtém o caminho completo do grupo (Pasta/Subpasta/...)"""
                if not group:
                    return ""
                path_parts = []
                current = group
                while current and current.name and current.name != "Root":
                    path_parts.insert(0, current.name)
                    current = current.parentgroup
                return "/".join(path_parts) if path_parts else ""

            def build_hierarchy_from_spaces(kp):
                """
                Constrói hierarquia baseada em espaços no início do nome.
                2 espaços = 1 nível de profundidade.
                Retorna dict: nome_original -> caminho_hierarquico
                """
                SPACES_PER_LEVEL = 2
                hierarchy_map = {}
                level_stack = []  # [(nivel, nome_limpo), ...]

                # Coletar todos os grupos (exceto Root)
                all_groups = []
                def collect_groups(group):
                    for subgroup in group.subgroups:
                        all_groups.append(subgroup.name)
                        collect_groups(subgroup)
                collect_groups(kp.root_group)

                # Ordenar para processar na ordem correta
                for group_name in all_groups:
                    if not group_name:
                        continue

                    # Contar espaços no início
                    stripped = group_name.lstrip(' ')
                    leading_spaces = len(group_name) - len(stripped)
                    level = leading_spaces // SPACES_PER_LEVEL
                    clean_name = stripped

                    # Atualizar pilha de níveis
                    while level_stack and level_stack[-1][0] >= level:
                        level_stack.pop()

                    # Construir caminho
                    if level_stack:
                        parent_path = "/".join([name for _, name in level_stack])
                        full_path = f"{parent_path}/{clean_name}"
                    else:
                        full_path = clean_name

                    hierarchy_map[group_name] = full_path
                    level_stack.append((level, clean_name))

                    print(f"[DEBUG] Grupo '{group_name}' -> '{full_path}' (nível {level})")

                return hierarchy_map

            # Construir mapa de hierarquia baseado em espaços
            hierarchy_map = build_hierarchy_from_spaces(kp)

            # Iterar por todas as entradas
            for entry in kp.entries:
                if entry.title:  # Ignorar entradas vazias
                    # Primeiro tenta hierarquia real
                    group_path = get_group_path(entry.group)

                    # Se o grupo está no mapa de espaços, usa o caminho convertido
                    if entry.group and entry.group.name in hierarchy_map:
                        group_path = hierarchy_map[entry.group.name]

                    print(f"[DEBUG] Entrada '{entry.title}' grupo: '{group_path}'")

                    entry_data = {
                        "type": "🔐 Senha",
                        "title": entry.title or "",
                        "username": entry.username or "",
                        "password": entry.password or "",
                        "url": entry.url or "",
                        "notes": entry.notes or "",
                        "group": group_path if group_path else "Importado",
                        "created": entry.ctime.strftime("%Y-%m-%d %H:%M") if entry.ctime else "",
                        "modified": entry.mtime.strftime("%Y-%m-%d %H:%M") if entry.mtime else "",
                        "tags": list(entry.tags) if entry.tags else [],
                    }
                    # Converter tags para string
                    if isinstance(entry_data["tags"], list):
                        entry_data["tags"] = ", ".join(entry_data["tags"])
                    self.imported_entries.append(entry_data)

            # Mostrar resultado
            self.show_import_result()

        except Exception as e:
            import traceback
            error_msg = str(e)
            error_type = type(e).__name__
            detailed_error = traceback.format_exc()
            print(f"[DEBUG] Erro: {detailed_error}")

            # Mensagem mais específica baseada no tipo de erro
            if "credentials" in error_msg.lower() or "CredentialsError" in error_type:
                QMessageBox.critical(self, "Credenciais Inválidas",
                    f"❌ Senha ou arquivo-chave incorretos!\n\n"
                    f"O arquivo foi encontrado e é um .kdbx válido,\n"
                    f"mas as credenciais não correspondem.\n\n"
                    f"Verifique:\n"
                    f"• A senha está correta?\n"
                    f"• Este é o arquivo-chave correto para este banco?\n"
                    f"• O banco usa APENAS senha ou senha+keyfile?")
            elif "xpath" in error_msg.lower():
                QMessageBox.critical(self, "Erro no Arquivo-chave",
                    f"❌ Problema ao processar o arquivo-chave.\n\n"
                    f"O pykeepass pode não suportar este tipo de keyfile.\n\n"
                    f"Tente:\n"
                    f"• Usar um keyfile .key ou .keyx padrão\n"
                    f"• Abrir no KeePassXC e exportar para CSV")
            else:
                QMessageBox.critical(self, "Erro ao Importar",
                    f"Não foi possível abrir o arquivo .kdbx.\n\n"
                    f"Arquivo: {file_path}\n"
                    f"Keyfile: {keyfile_path if keyfile_path else 'Nenhum'}\n\n"
                    f"Erro ({error_type}): {error_msg}")

    def import_other_format(self, file_path, format_idx):
        """Importa outros formatos (CSV, JSON, etc.)"""
        try:
            self.imported_entries = []

            if format_idx == 1:  # CSV
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # KeePassXC exporta com "Group" - preservar a estrutura
                        group = row.get("Group", row.get("group", row.get("Folder", "")))
                        if not group:
                            group = "Importado CSV"

                        # Detectar tipo baseado no grupo ou campos
                        entry_type = "🔐 Senha"
                        if "nota" in group.lower() or "note" in group.lower():
                            entry_type = "📝 Nota"
                        elif "cartão" in group.lower() or "card" in group.lower():
                            entry_type = "💳 Cartão"

                        entry = {
                            "type": entry_type,
                            "title": row.get("Title", row.get("title", row.get("name", ""))),
                            "username": row.get("Username", row.get("username", row.get("login", ""))),
                            "password": row.get("Password", row.get("password", "")),
                            "url": row.get("URL", row.get("url", row.get("website", ""))),
                            "notes": row.get("Notes", row.get("notes", "")),
                            "tags": row.get("Tags", row.get("tags", "")),
                            "group": group,
                            "created": row.get("Created", row.get("created", datetime.now().strftime("%Y-%m-%d %H:%M"))),
                            "modified": row.get("Modified", row.get("modified", datetime.now().strftime("%Y-%m-%d %H:%M"))),
                        }
                        if entry["title"] or entry["username"]:
                            self.imported_entries.append(entry)

                print(f"[DEBUG] CSV importado: {len(self.imported_entries)} entradas")

            elif format_idx == 2:  # Bitwarden JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    items = data.get("items", data.get("logins", []))
                    for item in items:
                        login = item.get("login", {})
                        entry = {
                            "type": "🔐 Senha",
                            "title": item.get("name", ""),
                            "username": login.get("username", item.get("username", "")),
                            "password": login.get("password", item.get("password", "")),
                            "url": login.get("uris", [{}])[0].get("uri", "") if login.get("uris") else item.get("url", ""),
                            "notes": item.get("notes", ""),
                            "group": "Importado Bitwarden",
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                        if entry["title"]:
                            self.imported_entries.append(entry)

            else:
                QMessageBox.warning(self, "Formato não suportado",
                    "Este formato ainda não está implementado.")
                return

            self.show_import_result()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar:\n{e}")

    def show_import_result(self):
        """Mostra o resultado da importação"""
        count = len(self.imported_entries)
        self.result_label.setText(
            f"<b>✅ {count} entradas encontradas!</b><br><br>"
            f"Revise as entradas abaixo e clique em 'Importar' para adicionar ao seu cofre."
        )

        # Preencher tabela de preview
        self.preview_table.setRowCount(0)
        for entry in self.imported_entries:
            row = self.preview_table.rowCount()
            self.preview_table.insertRow(row)
            self.preview_table.setItem(row, 0, QTableWidgetItem(entry.get("title", "")))
            self.preview_table.setItem(row, 1, QTableWidgetItem(entry.get("username", "")))
            self.preview_table.setItem(row, 2, QTableWidgetItem(entry.get("url", "")))
            self.preview_table.setItem(row, 3, QTableWidgetItem(entry.get("group", "")))

        self.stack.setCurrentIndex(2)
        self.back_btn.setEnabled(True)
        self.next_btn.setText("Importar")

    def finish_import(self):
        """Finaliza a importação adicionando as entradas"""
        if self.parent_window and hasattr(self.parent_window, 'entries'):
            self.parent_window.entries.extend(self.imported_entries)
            self.parent_window.is_modified = True
            self.parent_window.update_entries_table()

            if self.parent_window.is_locked:
                self.parent_window.is_locked = False
                self.parent_window.populate_groups()
                self.parent_window.central_stack.setCurrentIndex(1)

            QMessageBox.information(self, "Sucesso",
                f"✅ {len(self.imported_entries)} entradas importadas com sucesso!")

        self.accept()

    def get_imported_entries(self):
        return self.imported_entries


class SettingsDialog(QDialog):
    """Configurações estilo KeePassXC (Fotos 001-008)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configurações do Aplicativo")
        self.setMinimumSize(800, 550)

        layout = QHBoxLayout(self)

        # Lista de categorias (lateral esquerda)
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(150)
        self.category_list.setIconSize(QSize(24, 24))

        categories = [
            ("📋", "Geral"),
            ("🔒", "Segurança"),
            ("🌐", "Integração com\no Navegador"),
            (">_", "Agente SSH"),
            ("🔗", "KeeShare"),
        ]

        for icon, name in categories:
            item = QListWidgetItem(f"{icon} {name}")
            self.category_list.addItem(item)

        self.category_list.setCurrentRow(0)
        self.category_list.currentRowChanged.connect(self.change_category)
        layout.addWidget(self.category_list)

        # Área de conteúdo
        self.content_stack = QStackedWidget()

        # Página Geral
        general_page = self.create_general_page()
        self.content_stack.addWidget(general_page)

        # Página Segurança
        security_page = self.create_security_page()
        self.content_stack.addWidget(security_page)

        # Página Navegador
        browser_page = QWidget()
        browser_layout = QVBoxLayout(browser_page)
        browser_layout.addWidget(QLabel("Integração com navegador (em desenvolvimento)"))
        browser_layout.addStretch()
        self.content_stack.addWidget(browser_page)

        # Página SSH
        ssh_page = QWidget()
        ssh_layout = QVBoxLayout(ssh_page)
        ssh_layout.addWidget(QLabel("Agente SSH (em desenvolvimento)"))
        ssh_layout.addStretch()
        self.content_stack.addWidget(ssh_page)

        # Página KeeShare
        share_page = QWidget()
        share_layout = QVBoxLayout(share_page)
        share_layout.addWidget(QLabel("KeeShare (em desenvolvimento)"))
        share_layout.addStretch()
        self.content_stack.addWidget(share_page)

        layout.addWidget(self.content_stack)

        # Botões OK/Cancelar no rodapé
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryBtn")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Tempos limite
        timeout_group = QGroupBox("Tempos limite")
        timeout_layout = QVBoxLayout(timeout_group)

        cb1 = QCheckBox("Limpar área de transferência após")
        cb1.setChecked(True)
        timeout_layout.addWidget(cb1)

        cb2 = QCheckBox("Travar bancos de dados após inatividade de")
        cb2.setChecked(True)
        timeout_layout.addWidget(cb2)

        cb3 = QCheckBox("Limpar pesquisa depois de")
        timeout_layout.addWidget(cb3)

        layout.addWidget(timeout_group)

        # Opções de Bloqueio
        lock_group = QGroupBox("Opções de Bloqueio")
        lock_layout = QVBoxLayout(lock_group)

        lock_layout.addWidget(QCheckBox("Ativar desbloqueio rápido do banco de dados (Touch ID / Windows Hello)"))
        lock_layout.addWidget(QCheckBox("Bloqueio de bancos de dados quando a sessão estiver bloqueada ou a tampa está fechada"))
        lock_layout.addWidget(QCheckBox("Bloquear bancos de dados após minimizar a janela"))

        layout.addWidget(lock_group)

        layout.addStretch()
        return page

    def create_security_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # Conveniência
        conv_group = QGroupBox("Conveniência")
        conv_layout = QVBoxLayout(conv_group)

        conv_layout.addWidget(QCheckBox("Utilizar espaço reservado para campos de senha vazios"))
        conv_layout.addWidget(QCheckBox("Ocultar senhas ao editá-las"))
        conv_layout.addWidget(QCheckBox("Ocultar senhas no painel da prévia de entrada"))
        conv_layout.addWidget(QCheckBox("Ocultar TOTP no painel de visualização da entrada"))
        conv_layout.addWidget(QCheckBox("Ocultar notas no painel de visualização da entrada"))

        layout.addWidget(conv_group)

        # Privacidade
        priv_group = QGroupBox("Privacidade")
        priv_layout = QVBoxLayout(priv_group)
        priv_layout.addWidget(QCheckBox("Usar o serviço DuckDuckGo para baixar ícones de websites"))
        layout.addWidget(priv_group)

        layout.addStretch()
        return page

    def change_category(self, index):
        self.content_stack.setCurrentIndex(index)


class UnlockDialog(QDialog):
    """Diálogo para desbloquear cofre com suporte a keyfile"""

    def __init__(self, vault_name="Cofre", parent=None, show_keyfile=False):
        super().__init__(parent)
        self.vault_name = vault_name
        self.show_keyfile = show_keyfile
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Desbloquear Banco de Dados")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<h3>🔐 {self.vault_name}</h3>"))

        form = QFormLayout()

        # Senha
        pass_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Senha mestra")
        pass_layout.addWidget(self.password_edit)

        show_btn = QPushButton("👁️")
        show_btn.setMaximumWidth(40)
        show_btn.clicked.connect(self.toggle_password)
        pass_layout.addWidget(show_btn)

        form.addRow("Senha:", pass_layout)

        # Keyfile (opcional)
        if self.show_keyfile:
            keyfile_layout = QHBoxLayout()

            self.keyfile_check = QCheckBox()
            self.keyfile_check.toggled.connect(self.toggle_keyfile_ui)
            keyfile_layout.addWidget(self.keyfile_check)

            self.keyfile_edit = QLineEdit()
            self.keyfile_edit.setPlaceholderText("Selecione arquivo-chave (opcional)")
            self.keyfile_edit.setEnabled(False)
            keyfile_layout.addWidget(self.keyfile_edit)

            self.keyfile_browse = QPushButton("...")
            self.keyfile_browse.setMaximumWidth(40)
            self.keyfile_browse.setEnabled(False)
            self.keyfile_browse.clicked.connect(self.browse_keyfile)
            keyfile_layout.addWidget(self.keyfile_browse)

            form.addRow("Arquivo-chave:", keyfile_layout)

        layout.addLayout(form)

        # Info
        if self.show_keyfile:
            info = QLabel("💡 Marque a caixa se seu banco usa arquivo-chave além da senha.")
            info.setStyleSheet("color: #666; font-size: 11px;")
            info.setWordWrap(True)
            layout.addWidget(info)

        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = QPushButton("Desbloquear")
        ok_btn.setObjectName("primaryBtn")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Enter para desbloquear
        self.password_edit.returnPressed.connect(self.accept)

    def toggle_password(self):
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)

    def toggle_keyfile_ui(self, checked):
        if hasattr(self, 'keyfile_edit'):
            self.keyfile_edit.setEnabled(checked)
            self.keyfile_browse.setEnabled(checked)

    def browse_keyfile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo-chave", "",
            "Todos (*.*)"
        )
        if file_path:
            self.keyfile_edit.setText(file_path)

    def get_password(self):
        return self.password_edit.text()

    def get_keyfile(self):
        if self.show_keyfile and hasattr(self, 'keyfile_check'):
            if self.keyfile_check.isChecked() and self.keyfile_edit.text():
                return self.keyfile_edit.text()
        return None


class EntryDialog(QDialog):
    """Diálogo para criar/editar entrada com Editor Markdown"""

    def __init__(self, parent=None, entry_type="password", entry_data=None, all_tags=None):
        super().__init__(parent)
        self.entry_type = entry_type
        self.entry_data = entry_data or {}
        self.all_tags = all_tags or []

        # Habilitar botões de minimizar, maximizar e fechar
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Nova Entrada" if not self.entry_data else "Editar Entrada")
        self.setMinimumSize(700, 550)
        self.resize(850, 650)  # Tamanho inicial maior

        layout = QVBoxLayout(self)

        # Tabs para organização
        self.tabs = QTabWidget()

        # === Tab Geral ===
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Tipo de entrada
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["🔐 Senha", "📝 Nota", "💳 Cartão", "🔑 Chave SSH"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        general_layout.addLayout(type_layout)

        # Formulário
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Título da entrada")
        form.addRow("Título:", self.title_edit)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Usuário ou email")
        form.addRow("Usuário:", self.username_edit)

        # Senha
        pass_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.password_edit)

        show_btn = QPushButton("👁️")
        show_btn.setMaximumWidth(40)
        show_btn.clicked.connect(self.toggle_password)
        pass_layout.addWidget(show_btn)

        gen_btn = QPushButton("🎲")
        gen_btn.setMaximumWidth(40)
        gen_btn.clicked.connect(self.generate_password)
        pass_layout.addWidget(gen_btn)

        form.addRow("Senha:", pass_layout)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://...")
        form.addRow("URL:", self.url_edit)

        # Tags
        tags_layout = QHBoxLayout()
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("tag1, tag2, tag3 (separadas por vírgula)")
        tags_layout.addWidget(self.tags_edit)
        form.addRow("🏷️ Tags:", tags_layout)

        general_layout.addLayout(form)
        general_layout.addStretch()

        self.tabs.addTab(general_tab, "📋 Geral")

        # === Tab Notas (Markdown) ===
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)

        notes_label = QLabel("📝 Notas em Markdown (use [[link]] para criar backlinks)")
        notes_label.setStyleSheet("color: #666; font-style: italic;")
        notes_layout.addWidget(notes_label)

        self.markdown_editor = MarkdownEditor()
        notes_layout.addWidget(self.markdown_editor)

        self.tabs.addTab(notes_tab, "📝 Notas (Markdown)")

        # === Tab Avançado ===
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)

        self.created_label = QLabel(self.entry_data.get("created", "-"))
        advanced_layout.addRow("Criado em:", self.created_label)

        self.modified_label = QLabel(self.entry_data.get("modified", "-"))
        advanced_layout.addRow("Modificado em:", self.modified_label)

        # Backlinks encontrados
        backlinks_group = QGroupBox("🔗 Backlinks detectados")
        backlinks_layout = QVBoxLayout(backlinks_group)
        self.backlinks_list = QListWidget()
        self.backlinks_list.setMaximumHeight(100)
        backlinks_layout.addWidget(self.backlinks_list)
        advanced_layout.addRow(backlinks_group)

        self.tabs.addTab(advanced_tab, "⚙️ Avançado")

        layout.addWidget(self.tabs)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Salvar")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Carregar dados existentes
        if self.entry_data:
            self.title_edit.setText(self.entry_data.get("title", ""))
            self.username_edit.setText(self.entry_data.get("username", ""))
            self.password_edit.setText(self.entry_data.get("password", ""))
            self.url_edit.setText(self.entry_data.get("url", ""))
            self.tags_edit.setText(self.entry_data.get("tags", ""))
            self.markdown_editor.set_text(self.entry_data.get("notes", ""))

            # Selecionar tipo correto
            entry_type = self.entry_data.get("type", "")
            for i in range(self.type_combo.count()):
                if self.type_combo.itemText(i) == entry_type:
                    self.type_combo.setCurrentIndex(i)
                    break

        # Atualizar backlinks
        self.markdown_editor.editor.textChanged.connect(self.update_backlinks_list)

        # Garantir que campos estejam habilitados inicialmente
        self.on_type_changed(self.type_combo.currentText())

        # Enter em qualquer campo salva a entrada
        self.title_edit.returnPressed.connect(self.accept)
        self.username_edit.returnPressed.connect(self.accept)
        self.password_edit.returnPressed.connect(self.accept)
        self.url_edit.returnPressed.connect(self.accept)
        self.tags_edit.returnPressed.connect(self.accept)

    def on_type_changed(self, text):
        """Ajusta campos baseado no tipo selecionado"""
        is_note = "Nota" in text
        # Habilitar/desabilitar campos baseado no tipo
        self.username_edit.setEnabled(not is_note)
        self.password_edit.setEnabled(not is_note)
        self.url_edit.setEnabled(not is_note)

        # Sempre manter título e tags habilitados
        self.title_edit.setEnabled(True)
        self.tags_edit.setEnabled(True)

        if is_note:
            self.tabs.setCurrentIndex(1)  # Vai para aba de notas

    def update_backlinks_list(self):
        """Atualiza lista de backlinks detectados"""
        self.backlinks_list.clear()
        backlinks = self.markdown_editor.get_backlinks()
        for link in backlinks:
            self.backlinks_list.addItem(f"🔗 {link}")

    def toggle_password(self):
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)

    def generate_password(self):
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec_():
            self.password_edit.setText(dialog.get_password())

    def get_data(self):
        return {
            "type": self.type_combo.currentText(),
            "title": self.title_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "url": self.url_edit.text(),
            "notes": self.markdown_editor.get_text(),
            "tags": self.tags_edit.text(),
            "backlinks": self.markdown_editor.get_backlinks(),
            "created": self.entry_data.get("created", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M")
        }


class KeepsidianWindow(QMainWindow):
    """Janela principal do Keepsidian"""

    def __init__(self):
        super().__init__()
        self.entries = []
        self.current_file = None
        self.is_modified = False
        self.is_locked = True
        self.vault_password = None
        self.vault_keyfile = None
        self.vault_name = None

        # Inicializar gerenciador de IA
        self.ai_manager = AIManager()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(1100, 650)
        self.setStyleSheet(KEEPASS_STYLE)

        self.create_menu()
        self.create_toolbar()

        # Widget central com stack
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # Página 1: Welcome
        self.welcome_widget = WelcomeWidget(self)
        self.central_stack.addWidget(self.welcome_widget)

        # Página 2: Área principal
        self.main_widget = self.create_main_area()
        self.central_stack.addWidget(self.main_widget)

        # Mostrar Welcome inicialmente
        self.central_stack.setCurrentIndex(0)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()

    def create_menu(self):
        menubar = self.menuBar()

        # Menu Banco de dados
        db_menu = menubar.addMenu("Banco de dados")

        new_action = QAction("🆕 Novo banco de dados...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_vault)
        db_menu.addAction(new_action)

        open_action = QAction("📂 Abrir banco de dados...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_vault)
        db_menu.addAction(open_action)

        db_menu.addSeparator()

        save_action = QAction("💾 Salvar banco de dados", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_vault)
        db_menu.addAction(save_action)

        saveas_action = QAction("💾 Salvar banco de dados como...", self)
        saveas_action.setShortcut("Ctrl+Shift+S")
        saveas_action.triggered.connect(self.save_vault_as)
        db_menu.addAction(saveas_action)

        db_menu.addSeparator()

        import_action = QAction("📥 Importar...", self)
        import_action.triggered.connect(self.show_import_wizard)
        db_menu.addAction(import_action)

        export_action = QAction("📤 Exportar...", self)
        export_action.triggered.connect(self.export_vault)
        db_menu.addAction(export_action)

        db_menu.addSeparator()

        lock_action = QAction("🔒 Bloquear bancos de dados", self)
        lock_action.setShortcut("Ctrl+L")
        lock_action.triggered.connect(self.lock_vault)
        db_menu.addAction(lock_action)

        db_menu.addSeparator()

        exit_action = QAction("🚪 Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        db_menu.addAction(exit_action)

        # Menu Entradas
        entries_menu = menubar.addMenu("Entradas")

        add_entry = QAction("➕ Nova entrada", self)
        add_entry.setShortcut("Ctrl+N")
        add_entry.triggered.connect(self.add_entry)
        entries_menu.addAction(add_entry)

        edit_entry = QAction("✏️ Editar entrada", self)
        edit_entry.triggered.connect(self.edit_entry)
        entries_menu.addAction(edit_entry)

        delete_entry = QAction("🗑️ Excluir entrada", self)
        delete_entry.setShortcut("Delete")
        delete_entry.triggered.connect(self.delete_entry)
        entries_menu.addAction(delete_entry)

        entries_menu.addSeparator()

        copy_user = QAction("📋 Copiar nome de usuário", self)
        copy_user.setShortcut("Ctrl+B")
        copy_user.triggered.connect(self.copy_username)
        entries_menu.addAction(copy_user)

        copy_pass = QAction("📋 Copiar senha", self)
        copy_pass.setShortcut("Ctrl+C")
        copy_pass.triggered.connect(self.copy_password)
        entries_menu.addAction(copy_pass)

        # Menu Grupos
        groups_menu = menubar.addMenu("Grupos")

        add_group = QAction("📁 Novo grupo", self)
        add_group.triggered.connect(self.add_group)
        groups_menu.addAction(add_group)

        # Menu Ferramentas
        tools_menu = menubar.addMenu("Ferramentas")

        gen_password = QAction("🎲 Gerador de senhas", self)
        gen_password.triggered.connect(self.show_password_generator)
        tools_menu.addAction(gen_password)

        ai_query = QAction("🤖 Consultar IA", self)
        ai_query.setShortcut("Ctrl+I")
        ai_query.triggered.connect(self.show_ai_query)
        tools_menu.addAction(ai_query)

        ai_config = QAction("⚡ Configurar IAs", self)
        ai_config.triggered.connect(self.show_ai_config)
        tools_menu.addAction(ai_config)

        tools_menu.addSeparator()

        settings = QAction("⚙️ Configurações", self)
        settings.triggered.connect(self.show_settings)
        tools_menu.addAction(settings)

        # Menu Ver
        view_menu = menubar.addMenu("Ver")

        graph_action = QAction("🕸️ Graph View (Mapa de Conexões)", self)
        graph_action.setShortcut("Ctrl+G")
        graph_action.triggered.connect(self.show_graph_view)
        view_menu.addAction(graph_action)

        dashboard_action = QAction("📊 Dashboard de Status", self)
        dashboard_action.setShortcut("Ctrl+D")
        dashboard_action.triggered.connect(self.show_dashboard)
        view_menu.addAction(dashboard_action)

        # Menu Ajuda
        help_menu = menubar.addMenu("Ajuda")

        about = QAction(f"ℹ️ Sobre {APP_NAME}", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 1px;
                padding: 2px 4px;
                background-color: #fafafa;
                border-bottom: 1px solid #e0e0e0;
            }
            QToolButton {
                font-size: 14px;
                padding: 3px 5px;
                min-width: 24px;
                min-height: 24px;
                border: 1px solid transparent;
                border-radius: 3px;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #d0d0d0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #b0b0b0;
            }
            QToolButton:disabled {
                color: #c0c0c0;
                background-color: transparent;
            }
        """)
        self.addToolBar(toolbar)

        # Guardar referências dos botões para habilitar/desabilitar
        self.toolbar_actions = {}

        # === Grupo 1: Arquivo ===
        act = toolbar.addAction("📁")  # Abrir
        act.setToolTip("Abrir banco de dados (Ctrl+O)")
        act.triggered.connect(self.open_vault)

        act = toolbar.addAction("💾")  # Salvar
        act.setToolTip("Salvar banco de dados (Ctrl+S)")
        act.triggered.connect(self.save_vault)
        self.toolbar_actions['save'] = act

        act = toolbar.addAction("🔒")  # Bloquear com seta
        act.setToolTip("Bloquear banco de dados (Ctrl+L)")
        act.triggered.connect(self.lock_vault)
        self.toolbar_actions['lock'] = act

        toolbar.addSeparator()

        # === Grupo 2: Entradas ===
        act = toolbar.addAction("➕")  # Nova entrada
        act.setToolTip("Nova entrada (Ctrl+N)")
        act.triggered.connect(self.add_entry)
        self.toolbar_actions['add'] = act

        act = toolbar.addAction("✏️")  # Editar
        act.setToolTip("Editar entrada selecionada")
        act.triggered.connect(self.edit_entry)
        self.toolbar_actions['edit'] = act

        act = toolbar.addAction("🗑️")  # Excluir
        act.setToolTip("Excluir entrada selecionada (Delete)")
        act.triggered.connect(self.delete_entry)
        self.toolbar_actions['delete'] = act

        toolbar.addSeparator()

        # === Grupo 3: Copiar ===
        act = toolbar.addAction("👤")  # Copiar usuário
        act.setToolTip("Copiar nome de usuário (Ctrl+B)")
        act.triggered.connect(self.copy_username)
        self.toolbar_actions['copy_user'] = act

        act = toolbar.addAction("🔑")  # Copiar senha
        act.setToolTip("Copiar senha (Ctrl+C)")
        act.triggered.connect(self.copy_password)
        self.toolbar_actions['copy_pass'] = act

        act = toolbar.addAction("🌐")  # Abrir URL
        act.setToolTip("Abrir URL no navegador")
        act.triggered.connect(self.open_url)
        self.toolbar_actions['open_url'] = act

        toolbar.addSeparator()

        # === Grupo 4: Ferramentas ===
        act = toolbar.addAction("🎲")  # Gerador de senhas
        act.setToolTip("Gerador de senhas")
        act.triggered.connect(self.show_password_generator)

        act = toolbar.addAction("🕸️")  # Graph View
        act.setToolTip("Graph View - Mapa de Conexões (Ctrl+G)")
        act.triggered.connect(self.show_graph_view)
        self.toolbar_actions['graph'] = act

        act = toolbar.addAction("🤖")  # Consultar IA
        act.setToolTip("Consultar IA (Ctrl+I)")
        act.triggered.connect(self.show_ai_query)
        self.toolbar_actions['ai'] = act

        act = toolbar.addAction("📊")  # Dashboard
        act.setToolTip("Dashboard de Status (Ctrl+D)")
        act.triggered.connect(self.show_dashboard)
        self.toolbar_actions['dashboard'] = act

        toolbar.addSeparator()

        act = toolbar.addAction("🖥️")  # Tela cheia
        act.setToolTip("Alternar tela cheia")
        act.triggered.connect(self.toggle_fullscreen)

        act = toolbar.addAction("⚙️")  # Configurações
        act.setToolTip("Configurações")
        act.triggered.connect(self.show_settings)

        # === Espaçador ===
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # === Busca ===
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Pesquisar (Ctrl+F)...")
        self.search_input.setMinimumWidth(150)
        self.search_input.setMaximumWidth(220)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 3px 8px;
                font-size: 12px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #90caf9;
            }
        """)
        self.search_input.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_input)

        act = toolbar.addAction("❓")  # Ajuda
        act.setToolTip("Ajuda")
        act.triggered.connect(self.show_about)

        # Atualizar estado inicial dos botões
        self.update_toolbar_state()

    def update_toolbar_state(self):
        """Atualiza estado dos botões da toolbar baseado no estado do app"""
        is_unlocked = not self.is_locked
        has_selection = False

        if hasattr(self, 'entries_table'):
            has_selection = self.entries_table.currentRow() >= 0

        # Botões que requerem banco desbloqueado
        for key in ['save', 'lock', 'add']:
            if key in self.toolbar_actions:
                self.toolbar_actions[key].setEnabled(is_unlocked)

        # Botões que requerem seleção
        for key in ['edit', 'delete', 'copy_user', 'copy_pass', 'open_url']:
            if key in self.toolbar_actions:
                self.toolbar_actions[key].setEnabled(is_unlocked and has_selection)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_url(self):
        row = self.entries_table.currentRow()
        if row >= 0 and row < len(self.entries):
            url = self.entries[row].get("url", "")
            if url:
                import webbrowser
                webbrowser.open(url)

    def create_main_area(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # Painel esquerdo: Grupos
        self.groups_tree = QTreeWidget()
        self.groups_tree.setHeaderLabel("Grupos")
        self.groups_tree.setMinimumWidth(180)
        self.groups_tree.itemClicked.connect(self.on_group_selected)
        self.groups_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.groups_tree.customContextMenuRequested.connect(self.show_group_context_menu)

        # Drag & Drop para grupos
        self.groups_tree.setDragEnabled(True)
        self.groups_tree.setAcceptDrops(True)
        self.groups_tree.setDropIndicatorShown(True)
        self.groups_tree.setDragDropMode(QAbstractItemView.InternalMove)

        splitter.addWidget(self.groups_tree)

        # Painel central: Entradas
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(5)
        self.entries_table.setHorizontalHeaderLabels(["Tipo", "Título", "Usuário", "URL", "🏷️ Tags"])
        self.entries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.entries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.entries_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.entries_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.itemDoubleClicked.connect(self.edit_entry)
        self.entries_table.setMinimumWidth(400)

        # Menu de contexto para entradas
        self.entries_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entries_table.customContextMenuRequested.connect(self.show_entry_context_menu)

        # Drag & Drop para entradas
        self.entries_table.setDragEnabled(True)
        self.entries_table.setSelectionMode(QAbstractItemView.SingleSelection)

        splitter.addWidget(self.entries_table)

        # Painel direito: Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(5, 5, 5, 5)

        self.preview_tabs = QTabWidget()

        # Tab Geral
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        self.preview_label = QLabel("Selecione uma entrada")
        self.preview_label.setAlignment(Qt.AlignTop)
        general_layout.addWidget(self.preview_label)
        self.preview_tabs.addTab(general_tab, "Geral")

        # Tab Avançado
        self.preview_tabs.addTab(QWidget(), "Avançado")

        # Tab Ícone
        self.preview_tabs.addTab(QWidget(), "Ícone")

        # Tab Histórico
        self.preview_tabs.addTab(QWidget(), "Histórico")

        preview_layout.addWidget(self.preview_tabs)
        preview_widget.setMinimumWidth(250)
        splitter.addWidget(preview_widget)

        splitter.setSizes([180, 500, 300])
        layout.addWidget(splitter)

        return widget

    def populate_groups(self):
        """Popula árvore de grupos baseado nas entradas"""
        self.groups_tree.clear()

        root = QTreeWidgetItem(self.groups_tree, ["📁 Raiz"])
        root.setExpanded(True)

        # Coletar todos os grupos das entradas
        groups_set = set()
        for entry in self.entries:
            group = entry.get("group", "")
            if group:
                # Suportar hierarquia com / ou \
                parts = group.replace("\\", "/").split("/")
                for i in range(len(parts)):
                    groups_set.add("/".join(parts[:i+1]))

        # Criar estrutura hierárquica
        group_items = {"": root}

        for group_path in sorted(groups_set):
            if not group_path:
                continue

            parts = group_path.split("/")
            parent_path = "/".join(parts[:-1])
            group_name = parts[-1]

            parent_item = group_items.get(parent_path, root)

            # Escolher ícone baseado no nome
            if "senha" in group_name.lower() or "password" in group_name.lower():
                icon = "🔐"
            elif "nota" in group_name.lower() or "note" in group_name.lower():
                icon = "📝"
            elif "cartão" in group_name.lower() or "card" in group_name.lower():
                icon = "💳"
            elif "banco" in group_name.lower() or "bank" in group_name.lower():
                icon = "🏦"
            elif "email" in group_name.lower() or "mail" in group_name.lower():
                icon = "📧"
            elif "internet" in group_name.lower() or "web" in group_name.lower():
                icon = "🌐"
            else:
                icon = "📁"

            item = QTreeWidgetItem(parent_item, [f"{icon} {group_name}"])
            item.setExpanded(True)
            item.setData(0, Qt.UserRole, group_path)  # Guardar path completo
            group_items[group_path] = item

        # Se não houver grupos, criar estrutura padrão
        if not groups_set:
            passwords = QTreeWidgetItem(root, ["🔐 Senhas"])
            passwords.setExpanded(True)
            QTreeWidgetItem(passwords, ["📁 Internet"])
            QTreeWidgetItem(passwords, ["📁 Email"])
            QTreeWidgetItem(passwords, ["📁 Banco"])
            notes = QTreeWidgetItem(root, ["📝 Notas"])
            notes.setExpanded(True)

        recycle = QTreeWidgetItem(self.groups_tree, ["🗑️ Lixeira"])

    def new_vault(self):
        wizard = NewVaultWizard(self)
        if wizard.exec_():
            data = wizard.get_data()

            # Perguntar onde salvar o arquivo
            default_name = data.get("name", "NovoVault").replace(" ", "_")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar novo banco de dados",
                f"{default_name}.kdbx",
                "KeePass (*.kdbx);;Keepsidian JSON (*.kpsn)"
            )

            if not file_path:
                return  # Cancelado

            if not file_path.endswith(('.kdbx', '.kpsn')):
                file_path += '.kdbx'

            self.entries = []
            self.vault_password = data["password"]
            self.vault_keyfile = data.get("keyfile")
            self.vault_name = data.get("name", "Novo Banco")
            self._kp_instance = None

            # Criar arquivo .kdbx se for o formato escolhido
            if file_path.endswith('.kdbx'):
                if not PYKEEPASS_AVAILABLE:
                    QMessageBox.critical(self, "Erro",
                        "Biblioteca pykeepass não instalada!\n\n"
                        "Execute: pip install pykeepass")
                    return

                try:
                    kp = create_database(
                        file_path,
                        password=self.vault_password,
                        keyfile=self.vault_keyfile
                    )
                    kp.save()
                    self._kp_instance = kp
                    self.current_file = file_path
                except Exception as e:
                    QMessageBox.critical(self, "Erro",
                        f"Erro ao criar arquivo .kdbx:\n{str(e)}")
                    return
            else:
                self.current_file = file_path
                self._save_kpsn(file_path)

            self.is_locked = False
            self.populate_groups()
            self.update_entries_table()
            self.central_stack.setCurrentIndex(1)
            self.setWindowTitle(f"{APP_NAME} - {self.vault_name} v{VERSION}")

            msg = f"✅ Banco de dados criado!\n\n📁 {file_path}"
            if self.vault_keyfile:
                msg += f"\n\n🔑 Arquivo-chave:\n{self.vault_keyfile}"
            QMessageBox.information(self, "Sucesso", msg)

    def open_vault(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir banco de dados", "",
            "KeePass (*.kdbx);;Keepsidian (*.kpsn);;Todos (*.*)"
        )
        if file_path:
            if file_path.endswith('.kdbx'):
                self._open_kdbx(file_path)
            else:
                self._open_kpsn(file_path)

    def _open_kdbx(self, file_path):
        """Abre arquivo .kdbx usando pykeepass"""
        if not PYKEEPASS_AVAILABLE:
            QMessageBox.critical(self, "Erro",
                "Biblioteca pykeepass não instalada!\n\n"
                "Execute: pip install pykeepass")
            return

        print(f"[DEBUG] Abrindo .kdbx: {file_path}")

        dialog = UnlockDialog(Path(file_path).stem, self, show_keyfile=True)
        if dialog.exec_():
            try:
                password = dialog.get_password()
                keyfile = dialog.get_keyfile()

                print(f"[DEBUG] Senha fornecida: {'SIM' if password else 'NÃO'}")
                print(f"[DEBUG] Keyfile fornecido: {keyfile if keyfile else 'NÃO'}")

                # Abrir com pykeepass
                if keyfile and password:
                    print("[DEBUG] Modo: senha + keyfile")
                    kp = PyKeePass(file_path, password=password, keyfile=keyfile)
                elif keyfile:
                    print("[DEBUG] Modo: apenas keyfile")
                    kp = PyKeePass(file_path, password='', keyfile=keyfile)
                else:
                    print("[DEBUG] Modo: apenas senha")
                    kp = PyKeePass(file_path, password=password)

                print(f"[DEBUG] Banco aberto! Entradas: {len(kp.entries)}")

                def get_group_path(group):
                    """Obtém o caminho completo do grupo (Pasta/Subpasta/...)"""
                    if not group:
                        return ""
                    path_parts = []
                    current = group
                    while current and current.name and current.name != "Root":
                        path_parts.insert(0, current.name)
                        current = current.parentgroup
                    return "/".join(path_parts) if path_parts else ""

                def build_hierarchy_from_spaces(kp):
                    """
                    Constrói hierarquia baseada em espaços no início do nome.
                    2 espaços = 1 nível de profundidade.
                    Retorna dict: nome_original -> caminho_hierarquico
                    """
                    SPACES_PER_LEVEL = 2
                    hierarchy_map = {}
                    level_stack = []  # [(nivel, nome_limpo), ...]

                    # Coletar todos os grupos (exceto Root)
                    all_groups = []
                    def collect_groups(group):
                        for subgroup in group.subgroups:
                            all_groups.append(subgroup.name)
                            collect_groups(subgroup)
                    collect_groups(kp.root_group)

                    # Processar na ordem
                    for group_name in all_groups:
                        if not group_name:
                            continue

                        # Contar espaços no início
                        stripped = group_name.lstrip(' ')
                        leading_spaces = len(group_name) - len(stripped)
                        level = leading_spaces // SPACES_PER_LEVEL
                        clean_name = stripped

                        # Atualizar pilha de níveis
                        while level_stack and level_stack[-1][0] >= level:
                            level_stack.pop()

                        # Construir caminho
                        if level_stack:
                            parent_path = "/".join([name for _, name in level_stack])
                            full_path = f"{parent_path}/{clean_name}"
                        else:
                            full_path = clean_name

                        hierarchy_map[group_name] = full_path
                        level_stack.append((level, clean_name))

                        print(f"[DEBUG] Grupo '{group_name}' -> '{full_path}' (nível {level})")

                    return hierarchy_map

                # Construir mapa de hierarquia baseado em espaços
                hierarchy_map = build_hierarchy_from_spaces(kp)

                # Converter entradas
                self.entries = []
                for entry in kp.entries:
                    if entry.title:
                        # Converter tags de lista para string
                        tags_list = entry.tags if hasattr(entry, 'tags') and entry.tags else []
                        tags_str = ", ".join(tags_list) if tags_list else ""

                        # Obter caminho - primeiro tenta hierarquia real
                        group_path = get_group_path(entry.group)

                        # Se o grupo está no mapa de espaços, usa o caminho convertido
                        if entry.group and entry.group.name in hierarchy_map:
                            group_path = hierarchy_map[entry.group.name]

                        print(f"[DEBUG] Entrada '{entry.title}' grupo: '{group_path}'")

                        entry_data = {
                            "type": "🔐 Senha",
                            "title": entry.title or "",
                            "username": entry.username or "",
                            "password": entry.password or "",
                            "url": entry.url or "",
                            "notes": entry.notes or "",
                            "tags": tags_str,
                            "group": group_path if group_path else "",
                            "created": entry.ctime.strftime("%Y-%m-%d %H:%M") if entry.ctime else "",
                            "modified": entry.mtime.strftime("%Y-%m-%d %H:%M") if entry.mtime else "",
                        }
                        self.entries.append(entry_data)

                self.current_file = file_path
                self.vault_password = password
                self.vault_keyfile = keyfile
                self.vault_name = Path(file_path).stem
                self._kp_instance = kp  # Manter referência ao objeto PyKeePass
                self.is_locked = False
                self.populate_groups()
                self.update_entries_table()
                self.central_stack.setCurrentIndex(1)
                self.setWindowTitle(f"{APP_NAME} - {self.vault_name} v{VERSION}")

                QMessageBox.information(self, "Sucesso",
                    f"✅ Banco aberto: {self.vault_name}\n"
                    f"📊 {len(self.entries)} entradas carregadas")

            except Exception as e:
                import traceback
                error_msg = str(e)
                error_type = type(e).__name__
                print(f"[DEBUG] ERRO: {error_type}: {error_msg}")
                print(f"[DEBUG] {traceback.format_exc()}")

                # Mensagem específica por tipo de erro
                if "credentials" in error_msg.lower() or "CredentialsError" in error_type:
                    QMessageBox.critical(self, "Credenciais Inválidas",
                        f"❌ Senha ou arquivo-chave incorretos!\n\n"
                        f"Verifique:\n"
                        f"• A senha está correta?\n"
                        f"• Este banco usa arquivo-chave?\n"
                        f"• O arquivo-chave está correto?")
                elif "xpath" in error_msg.lower():
                    QMessageBox.critical(self, "Erro de Formato",
                        f"❌ Problema ao processar o arquivo.\n\n"
                        f"Este formato de .kdbx ou keyfile pode não ser suportado.\n\n"
                        f"Tente exportar do KeePassXC como CSV.")
                else:
                    QMessageBox.critical(self, "Erro ao Abrir .kdbx",
                        f"Não foi possível abrir o arquivo.\n\n"
                        f"Erro ({error_type}): {error_msg}")

    def _open_kpsn(self, file_path):
        """Abre arquivo .kpsn (formato JSON legado)"""
        dialog = UnlockDialog(Path(file_path).stem, self)
        if dialog.exec_():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.entries = data.get("entries", [])
                self.current_file = file_path
                self.vault_password = dialog.get_password()
                self.vault_keyfile = data.get("keyfile")
                self.vault_name = data.get("name", Path(file_path).stem)
                self.is_locked = False
                self.populate_groups()
                self.update_entries_table()
                self.central_stack.setCurrentIndex(1)
                self.setWindowTitle(f"{APP_NAME} - {self.vault_name} v{VERSION}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir: {e}")

    def save_vault(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_vault_as()

    def save_vault_as(self):
        # Sugerir nome baseado no vault atual
        suggested_name = getattr(self, 'vault_name', 'NovoVault') or 'NovoVault'

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Salvar banco de dados como",
            f"{suggested_name}.kdbx",
            "KeePass (*.kdbx);;Keepsidian JSON (*.kpsn)"
        )
        if file_path:
            if not file_path.endswith(('.kdbx', '.kpsn')):
                if 'kdbx' in selected_filter.lower():
                    file_path += '.kdbx'
                else:
                    file_path += '.kpsn'

            print(f"[DEBUG] Salvar Como: {file_path}")

            # IMPORTANTE: Limpar instância antiga para forçar criar novo arquivo
            old_kp = getattr(self, '_kp_instance', None)
            self._kp_instance = None

            # Salvar no novo arquivo
            self._save_to_file(file_path)

            # Atualizar nome e título
            self.current_file = file_path
            self.vault_name = Path(file_path).stem
            self.setWindowTitle(f"{APP_NAME} - {self.vault_name} v{VERSION}")

            print(f"[DEBUG] Novo arquivo: {self.current_file}")
            print(f"[DEBUG] Novo nome: {self.vault_name}")

    def _save_to_file(self, file_path):
        """Salva banco de dados - detecta formato pelo extensão"""
        if file_path.endswith('.kdbx'):
            self._save_kdbx(file_path)
        else:
            self._save_kpsn(file_path)

    def _save_kdbx(self, file_path):
        """Salva em formato .kdbx usando pykeepass"""
        if not PYKEEPASS_AVAILABLE:
            QMessageBox.critical(self, "Erro",
                "Biblioteca pykeepass não instalada!\n\n"
                "Execute: pip install pykeepass")
            return

        print(f"[DEBUG] Salvando .kdbx: {file_path}")
        print(f"[DEBUG] Entradas a salvar: {len(self.entries)}")

        def get_or_create_group(kp, group_path):
            """Obtém ou cria um grupo baseado no caminho (ex: 'Pasta/Subpasta')"""
            if not group_path or group_path in ('Root', 'root', ''):
                return kp.root_group

            parts = group_path.split('/')
            current_group = kp.root_group

            for part in parts:
                part = part.strip()
                if not part:
                    continue
                # Procurar subgrupo existente
                found = None
                for subgroup in current_group.subgroups:
                    if subgroup.name == part:
                        found = subgroup
                        break

                if found:
                    current_group = found
                else:
                    # Criar novo subgrupo
                    current_group = kp.add_group(current_group, part)
                    print(f"[DEBUG] Grupo criado: {part}")

            return current_group

        def find_entry_by_title_and_group(kp, title, group):
            """Busca entrada pelo título E grupo"""
            for entry in kp.entries:
                if entry.title == title and entry.group == group:
                    return entry
            return None

        try:
            # Se já temos uma instância do PyKeePass E é o mesmo arquivo, usar ela
            if hasattr(self, '_kp_instance') and self._kp_instance and self.current_file == file_path:
                kp = self._kp_instance
                print("[DEBUG] Usando instância existente")

                for entry_data in self.entries:
                    title = entry_data.get('title', '')
                    if not title:
                        continue

                    group_name = entry_data.get('group', '')
                    target_group = get_or_create_group(kp, group_name)

                    # Buscar entrada existente por título + grupo
                    existing_entry = find_entry_by_title_and_group(kp, title, target_group)

                    if existing_entry:
                        # Atualizar entrada existente
                        existing_entry.username = entry_data.get('username', '')
                        existing_entry.password = entry_data.get('password', '')
                        existing_entry.url = entry_data.get('url', '')
                        existing_entry.notes = entry_data.get('notes', '')
                        tags_str = entry_data.get('tags', '')
                        if tags_str:
                            existing_entry.tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                        else:
                            existing_entry.tags = []
                    else:
                        # Criar nova entrada no grupo correto
                        try:
                            new_entry = kp.add_entry(
                                target_group,
                                title=title,
                                username=entry_data.get('username', ''),
                                password=entry_data.get('password', ''),
                                url=entry_data.get('url', ''),
                                notes=entry_data.get('notes', '')
                            )
                            tags_str = entry_data.get('tags', '')
                            if tags_str:
                                new_entry.tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                        except Exception as e:
                            if "already exists" in str(e).lower():
                                # Se já existe, criar com sufixo numérico
                                suffix = 2
                                while True:
                                    new_title = f"{title} ({suffix})"
                                    try:
                                        new_entry = kp.add_entry(
                                            target_group,
                                            title=new_title,
                                            username=entry_data.get('username', ''),
                                            password=entry_data.get('password', ''),
                                            url=entry_data.get('url', ''),
                                            notes=entry_data.get('notes', '')
                                        )
                                        print(f"[DEBUG] Entrada duplicada renomeada: {new_title}")
                                        break
                                    except:
                                        suffix += 1
                                        if suffix > 100:
                                            break
                            else:
                                raise

                kp.save()
                print(f"[DEBUG] Salvo com sucesso usando instância existente")
            else:
                # Criar novo arquivo .kdbx
                print("[DEBUG] Criando novo arquivo .kdbx")

                # Pedir senha se não tiver
                password = self.vault_password
                if not password:
                    password, ok = QInputDialog.getText(
                        self, "Senha do Banco",
                        "Digite a senha para o novo arquivo .kdbx:",
                        QLineEdit.Password
                    )
                    if not ok or not password:
                        QMessageBox.warning(self, "Cancelado", "Salvamento cancelado - senha necessária.")
                        return
                    self.vault_password = password

                kp = create_database(
                    file_path,
                    password=password,
                    keyfile=self.vault_keyfile
                )

                # Adicionar todas as entradas com seus grupos
                for entry_data in self.entries:
                    title = entry_data.get('title', '')
                    if title:
                        group_name = entry_data.get('group', '')
                        target_group = get_or_create_group(kp, group_name)

                        try:
                            new_entry = kp.add_entry(
                                target_group,
                                title=title,
                                username=entry_data.get('username', ''),
                                password=entry_data.get('password', ''),
                                url=entry_data.get('url', ''),
                                notes=entry_data.get('notes', '')
                            )
                            tags_str = entry_data.get('tags', '')
                            if tags_str:
                                new_entry.tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                        except Exception as e:
                            if "already exists" in str(e).lower():
                                # Se já existe, criar com sufixo
                                suffix = 2
                                while suffix <= 100:
                                    new_title = f"{title} ({suffix})"
                                    try:
                                        new_entry = kp.add_entry(
                                            target_group,
                                            title=new_title,
                                            username=entry_data.get('username', ''),
                                            password=entry_data.get('password', ''),
                                            url=entry_data.get('url', ''),
                                            notes=entry_data.get('notes', '')
                                        )
                                        print(f"[DEBUG] Duplicada renomeada: {new_title}")
                                        break
                                    except:
                                        suffix += 1
                            else:
                                raise

                kp.save()
                self._kp_instance = kp
                print(f"[DEBUG] Novo arquivo criado com {len(self.entries)} entradas")

            self.is_modified = False
            self.current_file = file_path
            self.status_bar.showMessage(f"✅ Salvo: {file_path}", 3000)
            QMessageBox.information(self, "Salvo", f"✅ Arquivo salvo com sucesso!\n\n{file_path}")

        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Erro ao Salvar",
                f"Erro ao salvar arquivo .kdbx:\n\n{str(e)}")
            print(f"[DEBUG] {traceback.format_exc()}")

    def _save_kpsn(self, file_path):
        """Salva em formato .kpsn (JSON)"""
        try:
            data = {
                "version": VERSION,
                "created": datetime.now().isoformat(),
                "name": getattr(self, 'vault_name', None),
                "keyfile": getattr(self, 'vault_keyfile', None),
                "entries": self.entries
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.is_modified = False
            self.current_file = file_path
            self.status_bar.showMessage(f"✅ Salvo: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def show_import_wizard(self):
        wizard = ImportWizard(self)
        wizard.exec_()

    def export_vault(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar", "",
            "CSV (*.csv);;JSON (*.json)"
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    import csv
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=["title", "username", "password", "url", "notes"])
                        writer.writeheader()
                        writer.writerows(self.entries)
                else:
                    with open(file_path, 'w') as f:
                        json.dump(self.entries, f, indent=2)
                QMessageBox.information(self, "Sucesso", f"Exportado: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def lock_vault(self):
        self.is_locked = True
        self.central_stack.setCurrentIndex(0)
        self.update_status()

    def show_password_generator(self):
        dialog = PasswordGeneratorDialog(self)
        dialog.exec_()

    def show_ai_query(self):
        """Abre diálogo de consulta Multi-IA"""
        dialog = AIQueryDialog(self.ai_manager, self)
        dialog.exec_()

    def show_ai_config(self):
        """Abre configuração de APIs de IA"""
        dialog = AIConfigDialog(self.ai_manager, self)
        dialog.exec_()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_graph_view(self):
        """Abre o Graph View mostrando conexões entre entradas"""
        if self.is_locked:
            QMessageBox.warning(self, "Bloqueado", "Abra um banco de dados primeiro!")
            return

        if not self.entries:
            QMessageBox.information(self, "Graph View", "Nenhuma entrada para visualizar.\n\nCrie entradas e use [[backlinks]] nas notas para criar conexões.")
            return

        dialog = GraphDialog(self.entries, self)
        dialog.exec_()

    def show_dashboard(self):
        """Abre o Dashboard de Status e Monitoramento"""
        dialog = StatusDashboardDialog(
            parent=self,
            ai_manager=self.ai_manager,
            entries=self.entries
        )
        dialog.exec_()

    def show_about(self):
        QMessageBox.about(self, f"Sobre {APP_NAME}",
            f"<h2>{APP_NAME} v{VERSION}</h2>"
            "<p>Gerenciador de Senhas + Cofre de Conhecimento</p>"
            "<hr>"
            "<p><b>Funcionalidades:</b></p>"
            "<ul>"
            "<li>Gerenciamento de senhas (KeePassXC)</li>"
            "<li>Editor Markdown com preview</li>"
            "<li>Backlinks [[link]] estilo Obsidian</li>"
            "<li>Graph View de conexões</li>"
            "<li>Sistema de Tags</li>"
            "<li>🤖 Multi-IA (Ollama, Groq, OpenAI, Claude)</li>"
            "<li>📊 Dashboard de Status e Monitoramento</li>"
            "</ul>"
            "<hr>"
            "<p><b>CFDM AI OS TRIPLEX</b></p>"
            "<p>© 2024</p>"
        )

    def add_entry(self):
        if self.is_locked:
            QMessageBox.warning(self, "Bloqueado", "Abra ou crie um banco de dados primeiro!")
            return

        dialog = EntryDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            data["group"] = "Senhas"
            self.entries.append(data)
            self.is_modified = True
            self.update_entries_table()

    def edit_entry(self):
        row = self.entries_table.currentRow()
        if row >= 0 and row < len(self.entries):
            entry = self.entries[row]
            dialog = EntryDialog(self, entry_data=entry)
            if dialog.exec_():
                self.entries[row] = dialog.get_data()
                self.entries[row]["group"] = entry.get("group", "Senhas")
                self.is_modified = True
                self.update_entries_table()

    def delete_entry(self):
        row = self.entries_table.currentRow()
        if row >= 0 and row < len(self.entries):
            reply = QMessageBox.question(self, "Confirmar",
                f"Excluir '{self.entries[row]['title']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.entries[row]
                self.is_modified = True
                self.update_entries_table()

    def copy_username(self):
        row = self.entries_table.currentRow()
        if row >= 0 and row < len(self.entries):
            QApplication.clipboard().setText(self.entries[row].get("username", ""))
            self.status_bar.showMessage("Nome de usuário copiado!", 3000)

    def copy_password(self):
        row = self.entries_table.currentRow()
        if row >= 0 and row < len(self.entries):
            QApplication.clipboard().setText(self.entries[row].get("password", ""))
            self.status_bar.showMessage("Senha copiada!", 3000)

    def show_entry_context_menu(self, position):
        """Exibe menu de contexto para entradas"""
        row = self.entries_table.rowAt(position.y())
        if row < 0:
            return

        menu = QMenu()

        # Editar
        edit_action = menu.addAction("✏️ Editar entrada")
        edit_action.triggered.connect(self.edit_entry)

        # Clonar
        clone_action = menu.addAction("📋 Clonar entrada")
        clone_action.triggered.connect(lambda: self.clone_entry(row))

        menu.addSeparator()

        # Copiar
        copy_user = menu.addAction("👤 Copiar usuário")
        copy_user.triggered.connect(self.copy_username)

        copy_pass = menu.addAction("🔑 Copiar senha")
        copy_pass.triggered.connect(self.copy_password)

        copy_url = menu.addAction("🌐 Copiar URL")
        copy_url.triggered.connect(lambda: self.copy_entry_url(row))

        menu.addSeparator()

        # Mover para grupo
        move_menu = menu.addMenu("📦 Mover para grupo...")
        self._build_entry_move_menu(move_menu, row)

        menu.addSeparator()

        # Excluir
        delete_action = menu.addAction("🗑️ Excluir entrada")
        delete_action.triggered.connect(self.delete_entry)

        menu.exec_(self.entries_table.mapToGlobal(position))

    def _build_entry_move_menu(self, menu, entry_row):
        """Constrói submenu para mover entrada para grupos"""
        def add_group_items(parent_item, parent_menu, level=0):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                child_text = child.text(0)
                child_path = child.data(0, Qt.UserRole) or child_text.split(" ", 1)[-1]

                action = parent_menu.addAction("  " * level + child_text)
                action.triggered.connect(lambda checked, p=child_path: self.move_entry_to_group(entry_row, p))

                if child.childCount() > 0:
                    add_group_items(child, parent_menu, level + 1)

        # Adicionar Raiz
        root = self.groups_tree.topLevelItem(0)
        if root:
            root_action = menu.addAction("📁 Raiz")
            root_action.triggered.connect(lambda: self.move_entry_to_group(entry_row, "Root"))
            menu.addSeparator()
            add_group_items(root, menu)

    def move_entry_to_group(self, entry_row, group_path):
        """Move uma entrada para outro grupo"""
        if entry_row >= 0 and entry_row < len(self.entries):
            old_group = self.entries[entry_row].get("group", "")
            self.entries[entry_row]["group"] = group_path
            self.is_modified = True
            self.update_entries_table()
            self.status_bar.showMessage(f"Entrada movida para '{group_path}'!", 3000)

    def clone_entry(self, row):
        """Clona uma entrada"""
        if row >= 0 and row < len(self.entries):
            original = self.entries[row]
            clone = original.copy()
            clone["title"] = f"{original['title']} (cópia)"
            clone["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            clone["modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.entries.append(clone)
            self.is_modified = True
            self.update_entries_table()
            self.status_bar.showMessage(f"Entrada clonada!", 3000)

    def copy_entry_url(self, row):
        """Copia URL da entrada"""
        if row >= 0 and row < len(self.entries):
            url = self.entries[row].get("url", "")
            QApplication.clipboard().setText(url)
            self.status_bar.showMessage("URL copiada!", 3000)

    def show_group_context_menu(self, position):
        """Exibe menu de contexto para grupos"""
        item = self.groups_tree.itemAt(position)

        menu = QMenu()

        # Novo grupo
        new_action = menu.addAction("📁 Novo grupo")
        new_action.triggered.connect(self.add_group)

        # Novo subgrupo (só se tiver item selecionado)
        if item:
            new_sub_action = menu.addAction("📂 Novo subgrupo")
            new_sub_action.triggered.connect(lambda: self.add_subgroup(item))

        menu.addSeparator()

        if item:
            # Editar
            edit_action = menu.addAction("✏️ Renomear grupo")
            edit_action.triggered.connect(lambda: self.rename_group(item))

            # Clonar
            clone_action = menu.addAction("📋 Clonar grupo")
            clone_action.triggered.connect(lambda: self.clone_group(item))

            menu.addSeparator()

            # Mover
            move_menu = menu.addMenu("📦 Mover para...")
            self._build_move_menu(move_menu, item)

            menu.addSeparator()

            # Excluir
            delete_action = menu.addAction("🗑️ Excluir grupo")
            delete_action.triggered.connect(lambda: self.delete_group(item))

            # Não permitir excluir Raiz ou Lixeira
            item_text = item.text(0)
            if "Raiz" in item_text or "Lixeira" in item_text:
                delete_action.setEnabled(False)
                edit_action.setEnabled(False)

        menu.addSeparator()

        # Expandir/Colapsar todos
        expand_action = menu.addAction("➕ Expandir todos")
        expand_action.triggered.connect(self.groups_tree.expandAll)

        collapse_action = menu.addAction("➖ Colapsar todos")
        collapse_action.triggered.connect(self.groups_tree.collapseAll)

        menu.exec_(self.groups_tree.mapToGlobal(position))

    def _build_move_menu(self, menu, current_item):
        """Constrói submenu de mover para outros grupos"""
        def add_items(parent_item, parent_menu, level=0):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                if child != current_item:
                    child_text = child.text(0)
                    action = parent_menu.addAction("  " * level + child_text)
                    action.triggered.connect(lambda checked, c=child: self.move_group(current_item, c))

                    if child.childCount() > 0:
                        add_items(child, parent_menu, level + 1)

        # Adicionar Raiz como opção
        root = self.groups_tree.topLevelItem(0)
        if root and root != current_item:
            action = menu.addAction("📁 Raiz")
            action.triggered.connect(lambda: self.move_group(current_item, root))
            menu.addSeparator()
            add_items(root, menu)

    def add_group(self):
        """Adiciona novo grupo na raiz"""
        name, ok = QInputDialog.getText(self, "Novo Grupo", "Nome do grupo:")
        if ok and name:
            root = self.groups_tree.topLevelItem(0)  # Raiz
            if root:
                new_item = QTreeWidgetItem(root, [f"📁 {name}"])
                new_item.setData(0, Qt.UserRole, name)
                root.setExpanded(True)
                self.is_modified = True
                self.status_bar.showMessage(f"Grupo '{name}' criado!", 3000)

    def add_subgroup(self, parent_item):
        """Adiciona subgrupo dentro do grupo selecionado"""
        name, ok = QInputDialog.getText(self, "Novo Subgrupo", "Nome do subgrupo:")
        if ok and name:
            new_item = QTreeWidgetItem(parent_item, [f"📁 {name}"])
            parent_path = parent_item.data(0, Qt.UserRole) or ""
            new_path = f"{parent_path}/{name}" if parent_path else name
            new_item.setData(0, Qt.UserRole, new_path)
            parent_item.setExpanded(True)
            self.is_modified = True
            self.status_bar.showMessage(f"Subgrupo '{name}' criado!", 3000)

    def rename_group(self, item):
        """Renomeia um grupo"""
        old_name = item.text(0).split(" ", 1)[-1]  # Remove ícone
        new_name, ok = QInputDialog.getText(self, "Renomear Grupo", "Novo nome:", text=old_name)
        if ok and new_name and new_name != old_name:
            # Detectar ícone atual
            current_text = item.text(0)
            icon = current_text.split(" ")[0] if " " in current_text else "📁"
            item.setText(0, f"{icon} {new_name}")

            # Atualizar path
            old_path = item.data(0, Qt.UserRole) or old_name
            new_path = old_path.rsplit("/", 1)
            new_path = f"{new_path[0]}/{new_name}" if len(new_path) > 1 else new_name
            item.setData(0, Qt.UserRole, new_path)

            # Atualizar entradas que usam este grupo
            for entry in self.entries:
                if entry.get("group", "").startswith(old_path):
                    entry["group"] = entry["group"].replace(old_path, new_path, 1)

            self.is_modified = True
            self.status_bar.showMessage(f"Grupo renomeado para '{new_name}'!", 3000)

    def clone_group(self, item):
        """Clona um grupo com todas as entradas"""
        old_name = item.text(0).split(" ", 1)[-1]
        new_name, ok = QInputDialog.getText(self, "Clonar Grupo", "Nome do clone:", text=f"{old_name} (cópia)")
        if ok and new_name:
            parent = item.parent() or self.groups_tree.invisibleRootItem()
            new_item = QTreeWidgetItem(parent, [f"📁 {new_name}"])

            old_path = item.data(0, Qt.UserRole) or old_name
            new_path = old_path.rsplit("/", 1)
            new_path = f"{new_path[0]}/{new_name}" if len(new_path) > 1 else new_name
            new_item.setData(0, Qt.UserRole, new_path)

            # Clonar entradas do grupo
            cloned_count = 0
            for entry in self.entries[:]:  # Cópia para iterar
                if entry.get("group", "") == old_path:
                    new_entry = entry.copy()
                    new_entry["group"] = new_path
                    new_entry["title"] = f"{entry['title']} (cópia)"
                    self.entries.append(new_entry)
                    cloned_count += 1

            self.is_modified = True
            self.update_entries_table()
            self.status_bar.showMessage(f"Grupo clonado! {cloned_count} entradas copiadas.", 3000)

    def move_group(self, item, new_parent):
        """Move um grupo para outro local"""
        old_parent = item.parent()
        if old_parent:
            old_parent.removeChild(item)
        else:
            index = self.groups_tree.indexOfTopLevelItem(item)
            self.groups_tree.takeTopLevelItem(index)

        new_parent.addChild(item)
        new_parent.setExpanded(True)

        # Atualizar path
        group_name = item.text(0).split(" ", 1)[-1]
        parent_path = new_parent.data(0, Qt.UserRole) or ""
        new_path = f"{parent_path}/{group_name}" if parent_path else group_name
        old_path = item.data(0, Qt.UserRole) or group_name
        item.setData(0, Qt.UserRole, new_path)

        # Atualizar entradas
        for entry in self.entries:
            if entry.get("group", "").startswith(old_path):
                entry["group"] = entry["group"].replace(old_path, new_path, 1)

        self.is_modified = True
        self.status_bar.showMessage(f"Grupo movido!", 3000)

    def delete_group(self, item):
        """Exclui um grupo (move entradas para Raiz)"""
        group_name = item.text(0).split(" ", 1)[-1]
        group_path = item.data(0, Qt.UserRole) or group_name

        # Contar entradas afetadas
        affected = sum(1 for e in self.entries if e.get("group", "").startswith(group_path))

        reply = QMessageBox.question(self, "Excluir Grupo",
            f"Excluir grupo '{group_name}'?\n\n"
            f"⚠️ {affected} entradas serão movidas para 'Raiz'.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Mover entradas para Raiz
            for entry in self.entries:
                if entry.get("group", "").startswith(group_path):
                    entry["group"] = "Root"

            # Remover item da árvore
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.groups_tree.indexOfTopLevelItem(item)
                self.groups_tree.takeTopLevelItem(index)

            self.is_modified = True
            self.update_entries_table()
            self.status_bar.showMessage(f"Grupo '{group_name}' excluído!", 3000)

    def update_entries_table(self, filter_text=None, tag_filter=None, group_filter=None):
        self.entries_table.setRowCount(0)

        for entry in self.entries:
            # Filtro por grupo
            if group_filter:
                entry_group = entry.get("group", "").replace("\\", "/")
                if group_filter == "__trash__":
                    continue  # TODO: implementar lixeira
                # Mostrar entradas do grupo e subgrupos
                if not entry_group.startswith(group_filter):
                    continue

            # Filtro de texto (busca em título, usuário, URL e tags)
            if filter_text:
                search_str = f"{entry.get('title','')} {entry.get('username','')} {entry.get('url','')} {entry.get('tags','')}".lower()
                if filter_text.lower() not in search_str:
                    continue

            # Filtro por tag específica
            if tag_filter:
                entry_tags = [t.strip().lower() for t in entry.get("tags", "").split(",") if t.strip()]
                if tag_filter.lower() not in entry_tags:
                    continue

            row = self.entries_table.rowCount()
            self.entries_table.insertRow(row)

            # Tipo (ícone)
            entry_type = entry.get("type", "🔐 Senha")
            type_icon = entry_type.split()[0] if entry_type else "🔐"
            type_item = QTableWidgetItem(type_icon)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.entries_table.setItem(row, 0, type_item)

            # Título
            self.entries_table.setItem(row, 1, QTableWidgetItem(entry.get("title", "")))

            # Usuário
            self.entries_table.setItem(row, 2, QTableWidgetItem(entry.get("username", "")))

            # URL
            self.entries_table.setItem(row, 3, QTableWidgetItem(entry.get("url", "")))

            # Tags (formatadas)
            tags = entry.get("tags", "")
            if tags:
                tags_display = ", ".join([f"🏷️{t.strip()}" for t in tags.split(",") if t.strip()][:3])
                if len(tags.split(",")) > 3:
                    tags_display += "..."
            else:
                tags_display = ""
            self.entries_table.setItem(row, 4, QTableWidgetItem(tags_display))

        self.update_status()

    def update_status(self):
        if self.is_locked:
            self.status_bar.showMessage(f"🔒 Nenhum banco de dados aberto | v{VERSION}")
        else:
            total = len(self.entries)
            modified = " *" if self.is_modified else ""
            self.status_bar.showMessage(f"🔓 Entradas: {total}{modified} | v{VERSION}")

        # Atualizar estado dos botões da toolbar
        if hasattr(self, 'toolbar_actions'):
            self.update_toolbar_state()

    def on_group_selected(self, item):
        """Filtra entradas pelo grupo selecionado"""
        if item:
            group_path = item.data(0, Qt.UserRole)  # Path completo guardado
            if group_path:
                self.update_entries_table(group_filter=group_path)
            else:
                # Clicou em Raiz ou Lixeira
                item_text = item.text(0)
                if "Raiz" in item_text:
                    self.update_entries_table()  # Mostrar todas
                elif "Lixeira" in item_text:
                    self.update_entries_table(group_filter="__trash__")
                else:
                    self.update_entries_table()
        else:
            self.update_entries_table()

    def on_search(self, text):
        self.update_entries_table(filter_text=text if text else None)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = KeepsidianWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
