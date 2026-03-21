# KEEPSIDIAN - Arquitetura do Projeto

## Visão Geral

Keepsidian = KeePassXC + Cofre de Conhecimento (estilo Obsidian)

**Base:** KeePassXC (C++ / Qt)
**Licença:** GPLv3 (mantém compatibilidade)

---

## Componentes do KeePassXC (Base)

### Janela Principal (`MainWindow`)
- **Arquivo:** `src/gui/MainWindow.cpp` (97KB)
- **UI:** `src/gui/MainWindow.ui` (40KB)
- Contém: Menu, Toolbar, StatusBar, Tabs

### Widget de Banco de Dados (`DatabaseWidget`)
- **Arquivo:** `src/gui/DatabaseWidget.cpp` (90KB)
- Painel principal com lista de entradas
- Árvore de grupos à esquerda
- Lista de entradas à direita

### Busca (`SearchWidget`)
- **Arquivo:** `src/gui/SearchWidget.cpp`
- **UI:** `src/gui/SearchWidget.ui`
- Barra de busca com filtros

### Preview de Entrada (`EntryPreviewWidget`)
- **Arquivo:** `src/gui/EntryPreviewWidget.cpp`
- **UI:** `src/gui/EntryPreviewWidget.ui` (46KB)
- Mostra detalhes da entrada selecionada

### Gerador de Senhas (`PasswordGeneratorWidget`)
- **Arquivo:** `src/gui/PasswordGeneratorWidget.cpp`
- **UI:** `src/gui/PasswordGeneratorWidget.ui` (37KB)

### Tela de Boas-vindas (`WelcomeWidget`)
- **Arquivo:** `src/gui/WelcomeWidget.cpp`
- **UI:** `src/gui/WelcomeWidget.ui`

### Subdiretórios Importantes
```
src/gui/
├── entry/          # Edição de entradas
├── group/          # Edição de grupos
├── widgets/        # Widgets customizados
├── styles/         # Temas e estilos
├── databasekey/    # Chaves do banco
├── dbsettings/     # Configurações do banco
├── reports/        # Relatórios
└── wizard/         # Assistentes
```

---

## Modificações para Keepsidian

### 1. Novo Painel: Cofre de Conhecimento

```
┌─────────────────────────────────────────────────────────────────┐
│  Menu  │  Arquivo  │  Editar  │  Ver  │  Ferramentas  │  Ajuda │
├─────────────────────────────────────────────────────────────────┤
│  [Toolbar: Novo | Abrir | Salvar | Buscar | ...]               │
├────────────┬────────────────────────┬───────────────────────────┤
│            │                        │                           │
│  GRUPOS    │   LISTA DE ENTRADAS    │   PREVIEW / EDITOR        │
│  (árvore)  │   (senhas + notas)     │   (detalhes)              │
│            │                        │                           │
│  📁 Senhas │   🔐 Login Site A      │   ┌─────────────────────┐ │
│  📁 Cartões│   🔐 Login Site B      │   │ Título: Site A      │ │
│  📁 Notas  │   📝 Nota Projeto X    │   │ User: admin         │ │
│  📁 Chaves │   📝 Nota Reunião      │   │ Pass: ****          │ │
│            │   🔑 SSH Server        │   │ URL: https://...    │ │
│            │                        │   │                     │ │
│  ──────────│                        │   │ [NOTAS MARKDOWN]    │ │
│  📊 GRAFO  │                        │   │ # Anotações         │ │
│  🔗 LINKS  │                        │   │ - Item 1            │ │
│            │                        │   │ - Item 2            │ │
│            │                        │   └─────────────────────┘ │
├────────────┴────────────────────────┴───────────────────────────┤
│  [StatusBar: Entradas: 45 | Cofre: Desbloqueado | Sync: OK]    │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Novos Arquivos a Criar

```
src/gui/
├── KnowledgeWidget.cpp/.h/.ui      # Painel de notas/conhecimento
├── MarkdownEditor.cpp/.h/.ui       # Editor Markdown
├── GraphWidget.cpp/.h/.ui          # Visualização de grafo
├── LinkWidget.cpp/.h/.ui           # Gerenciador de links
├── NoteEntry.cpp/.h                # Tipo de entrada: Nota
└── keepsidian/
    ├── KnowledgeVault.cpp/.h       # Cofre de conhecimento
    ├── MarkdownParser.cpp/.h       # Parser Markdown
    ├── BiDirectionalLinks.cpp/.h   # Links bidirecionais
    └── TagManager.cpp/.h           # Gerenciador de tags
```

### 3. Modificações em Arquivos Existentes

| Arquivo | Modificação |
|---------|-------------|
| `MainWindow.cpp` | Adicionar painel de conhecimento |
| `MainWindow.ui` | Novo layout com split view |
| `DatabaseWidget.cpp` | Suporte a entradas de nota |
| `EntryPreviewWidget.cpp` | Renderização Markdown |
| `SearchWidget.cpp` | Busca em notas + senhas |

### 4. Novas Funcionalidades

#### 4.1 Editor Markdown
- Syntax highlighting
- Preview em tempo real
- Suporte a tabelas, código, listas
- Links internos `[[nota]]`

#### 4.2 Links Bidirecionais
- Detectar `[[links]]` automaticamente
- Backlinks (referências inversas)
- Grafo de conexões

#### 4.3 Tags e Categorias
- `#tag` em qualquer lugar
- Filtro por tags
- Nuvem de tags

#### 4.4 Dois Cofres Separados
```cpp
class Keepsidian {
    PasswordVault* passwordVault;    // Cofre de senhas (criptografia forte)
    KnowledgeVault* knowledgeVault;  // Cofre de notas (criptografia leve)
};
```

---

## Dependências Adicionais

```cmake
# CMakeLists.txt - adicionar
find_package(Qt5 COMPONENTS WebEngine REQUIRED)  # Para preview Markdown
find_package(cmark REQUIRED)                      # Parser Markdown
```

---

## Esquema de Cores (Customizável)

```css
/* Tema Keepsidian Dark */
--bg-primary: #1a1a2e;
--bg-secondary: #16213e;
--accent: #e94560;
--text: #eaeaea;
--text-muted: #8b8b8b;
--success: #00bf63;
--warning: #ffc107;
```

---

## Roadmap

### Fase 1: Fork e Compilação
- [ ] Fork do KeePassXC
- [ ] Configurar build
- [ ] Compilar e testar

### Fase 2: Modificações Básicas
- [ ] Renomear para Keepsidian
- [ ] Novo ícone e branding
- [ ] Tema de cores customizado

### Fase 3: Editor Markdown
- [ ] Criar MarkdownEditor widget
- [ ] Integrar cmark parser
- [ ] Preview em tempo real

### Fase 4: Cofre de Conhecimento
- [ ] Novo tipo de entrada: Nota
- [ ] Painel lateral de notas
- [ ] Sistema de tags

### Fase 5: Links e Grafo
- [ ] Parser de `[[links]]`
- [ ] Backlinks automáticos
- [ ] Visualização em grafo

### Fase 6: Polimento
- [ ] Temas customizáveis
- [ ] Sync (opcional)
- [ ] Plugins

---

## Comandos de Build

```bash
# Instalar dependências (Ubuntu)
sudo apt install build-essential cmake qtbase5-dev qttools5-dev \
    qttools5-dev-tools libqt5svg5-dev libargon2-dev libminizip-dev \
    libqt5x11extras5-dev libxi-dev libxtst-dev libqrencode-dev \
    libbotan-2-dev

# Compilar
cd keepsidian/source
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# Executar
./src/keepassxc
```
