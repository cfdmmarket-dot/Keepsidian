# Keepsidian - Lista de Funcionalidades

## Gerenciamento de Senhas (KeePassXC)

### Banco de Dados
- [x] Criar novo banco .kdbx
- [x] Abrir banco .kdbx existente
- [x] Salvar banco .kdbx
- [x] Salvar Como (novo arquivo)
- [x] Suporte a arquivo-chave (keyfile)
- [x] Bloquear banco (Ctrl+L)

### Entradas
- [x] Criar nova entrada
- [x] Editar entrada existente
- [x] Clonar entrada
- [x] Excluir entrada
- [x] Mover entrada para outro grupo
- [x] Copiar usuario (Ctrl+B)
- [x] Copiar senha (Ctrl+C)
- [x] Copiar URL

### Grupos
- [x] Criar novo grupo
- [x] Criar subgrupo
- [x] Renomear grupo
- [x] Clonar grupo
- [x] Mover grupo
- [x] Excluir grupo
- [x] Arrastar e soltar grupos
- [x] Hierarquia de grupos (Pasta/Subpasta)

### Tipos de Entrada
- [x] Senha (usuario + senha + URL)
- [x] Nota (Markdown)
- [x] Cartao (numero, validade, CVV)
- [x] Documento (tipo, numero, emissor)
- [x] Identidade (dados pessoais)

---

## Cofre de Conhecimento (Obsidian)

### Editor Markdown
- [x] Editor de texto com syntax highlight
- [x] Preview em tempo real
- [x] Formatacao basica (negrito, italico, etc)

### Backlinks
- [x] Suporte a `[[link]]`
- [x] Navegacao entre notas
- [x] Deteccao automatica de backlinks

### Tags
- [x] Adicionar tags as entradas
- [x] Salvar/carregar tags em .kdbx
- [x] Filtrar por tags

### Graph View
- [x] Visualizacao de conexoes
- [x] Grafo interativo
- [x] Atalho: Ctrl+G

---

## Integracao Multi-IA

### Provedores
- [x] Ollama (local)
- [x] Groq
- [x] OpenAI
- [x] Anthropic (Claude)

### Funcionalidades
- [x] Consulta simultanea a multiplos provedores
- [x] Atalho: Ctrl+I
- [x] Resposta formatada em Markdown

---

## Dashboard de Monitoramento

### Monitor de Sistema
- [x] Uso de CPU
- [x] Uso de Memoria
- [x] Uso de Disco

### Status de IA
- [x] Status de cada provedor
- [x] Indicador online/offline

### Estatisticas do Vault
- [x] Total de entradas
- [x] Total de tags
- [x] Total de backlinks

### Log de Atividades
- [x] Registro em tempo real
- [x] Auto-refresh

---

## Importacao/Exportacao

### Importar
- [x] KeePass .kdbx
- [x] CSV (KeePassXC format)
- [x] Bitwarden JSON
- [x] Preview antes de importar
- [x] Preservar grupos originais

### Exportar
- [ ] CSV
- [ ] JSON
- [ ] PDF (planejado)

---

## Interface

### Atalhos de Teclado
| Atalho | Acao |
|--------|------|
| Ctrl+N | Novo banco de dados |
| Ctrl+O | Abrir banco de dados |
| Ctrl+S | Salvar |
| Ctrl+L | Bloquear banco |
| Ctrl+G | Graph View |
| Ctrl+D | Dashboard |
| Ctrl+I | Consultar IA |
| Ctrl+F | Buscar |
| Ctrl+B | Copiar usuario |
| Ctrl+C | Copiar senha |

### Menus de Contexto
- [x] Menu de contexto para grupos (botao direito)
- [x] Menu de contexto para entradas (botao direito)

### Layout
- [x] Arvore de grupos (esquerda)
- [x] Tabela de entradas (centro)
- [x] Editor de notas (direita)
- [x] Barra de status

---

## Seguranca

- [x] Criptografia AES-256 (via pykeepass)
- [x] Suporte a arquivo-chave
- [x] Bloqueio automatico (planejado)
- [x] Limpeza de clipboard (planejado)

---

## Proximas Features (Roadmap)

- [ ] Modo escuro
- [ ] Sincronizacao com nuvem
- [ ] Plugins/extensoes
- [ ] Busca avancada com filtros
- [ ] Exportacao para PDF
- [ ] TOTP/2FA integrado
- [ ] Auto-type
