# Keepsidian

**Gerenciador de Senhas + Cofre de Conhecimento**

Combinando o melhor do KeePassXC com a filosofia do Obsidian, integrado ao projeto CFDM AI OS TRIPLEX.

![Version](https://img.shields.io/badge/version-0.2.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Funcionalidades

### Gerenciamento de Senhas (KeePassXC)
- Suporte nativo a arquivos `.kdbx`
- Criar, abrir e salvar bancos de dados KeePass
- Suporte a arquivo-chave (keyfile)
- Gerador de senhas seguras
- Copiar usuário/senha para área de transferência

### Cofre de Conhecimento (Obsidian)
- Editor Markdown com preview em tempo real
- Suporte a backlinks `[[link]]`
- Sistema de Tags
- Graph View - mapa visual de conexões entre entradas

### Integração Multi-IA
- Ollama (local)
- Groq
- OpenAI
- Anthropic (Claude)
- Consulta simultânea a múltiplos provedores

### Dashboard de Monitoramento
- Status do sistema (CPU, Memória, Disco)
- Status dos provedores de IA
- Estatísticas do vault
- Log de atividades em tempo real

## Instalação

### Requisitos
```bash
# PyQt5 (interface gráfica)
sudo apt-get install python3-pyqt5

# pykeepass (suporte .kdbx)
pip install pykeepass

# Opcional: markdown e requests
pip install markdown requests
```

### Executar
```bash
python3 keepsidian.py
```

## Changelog

### v0.2.0-alpha (Atual)
- **SUPORTE NATIVO A .KDBX** (criar, abrir, salvar)
- Diálogo de desbloqueio com suporte a arquivo-chave
- Importação CSV preservando grupos/pastas
- Árvore de grupos dinâmica
- Filtro por grupo na tabela de entradas
- Mensagens de erro mais específicas

### v0.1.9-alpha
- Dashboard de Status e Monitoramento (Ctrl+D)
- Monitor de Sistema (CPU, Memória, Disco)
- Status dos provedores de IA em tempo real
- Estatísticas do Vault (entradas, tags, backlinks)
- Log de atividades com auto-refresh

### v0.1.8-alpha
- Editor Markdown com Preview em tempo real
- Suporte a backlinks [[nota]]
- Sistema de Tags
- Graph View (mapa de conexões)
- Integração Multi-IA (Ollama, Groq, OpenAI, Anthropic)

### v0.1.7-alpha e anteriores
- Interface base estilo KeePassXC
- Gerenciamento básico de entradas
- Sistema de grupos
- Importação de arquivos

## Estrutura do Projeto

```
keepsidian/
├── keepsidian.py      # Aplicação principal
├── README.md          # Este arquivo
├── requirements.txt   # Dependências Python
└── .gitignore        # Arquivos ignorados pelo git
```

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| Ctrl+N | Novo banco de dados |
| Ctrl+O | Abrir banco de dados |
| Ctrl+S | Salvar |
| Ctrl+L | Bloquear banco |
| Ctrl+G | Graph View |
| Ctrl+D | Dashboard |
| Ctrl+I | Consultar IA |
| Ctrl+F | Buscar |
| Ctrl+B | Copiar usuário |
| Ctrl+C | Copiar senha |

## CFDM AI OS TRIPLEX

Este projeto faz parte do ecossistema **CFDM AI OS TRIPLEX**, uma plataforma de IA integrada que combina:
- Gerenciamento de conhecimento
- Automação com agentes IA
- Integração com múltiplos provedores de IA

## Licença

MIT License - Veja LICENSE para mais detalhes.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

---

**CFDM AI OS TRIPLEX** - 2024
