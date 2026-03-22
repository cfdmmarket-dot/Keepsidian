# Keepsidian - Diario de Desenvolvimento

## Visao Geral
Keepsidian e um gerenciador de senhas + cofre de conhecimento que combina:
- **KeePassXC**: Suporte nativo a arquivos `.kdbx`
- **Obsidian**: Editor Markdown com backlinks e Graph View
- **Multi-IA**: Integracao com Ollama, Groq, OpenAI, Anthropic

---

## Versao Atual: v0.2.5-alpha

### 2024 - Desenvolvimento Ativo

#### v0.2.5-alpha (Atual)
- **CORRECAO**: Grupos sao criados ao importar/salvar .kdbx
- **CORRECAO**: Entradas duplicadas recebem sufixo numerico automatico
- Suporte a hierarquia de grupos (Pasta/Subpasta)

#### v0.2.4-alpha
- **CORRECAO**: "Salvar Como" cria novo arquivo corretamente
- **CORRECAO**: Nome do arquivo atualiza no titulo da aplicacao
- Limpa instancia .kdbx antiga para forcar novo arquivo

#### v0.2.3-alpha
- Salvar Como pede senha se necessario
- Tags sao atualizadas ao salvar
- Confirmacao visual ao salvar arquivo

#### v0.2.2-alpha
- Menu de contexto para ENTRADAS (botao direito)
- Arrastar e soltar grupos na arvore
- Mover entradas para qualquer grupo via menu
- Clonar entradas

#### v0.2.1-alpha
- Menu de contexto completo para GRUPOS
- Tags salvam/carregam corretamente em .kdbx
- Dialogo de entrada com botoes min/max/fechar
- Enter salva em qualquer campo do formulario

#### v0.2.0-alpha
- **SUPORTE NATIVO A .KDBX** (criar, abrir, salvar)
- Dialogo de desbloqueio com suporte a arquivo-chave
- Compatibilidade total com KeePassXC

#### v0.1.9-alpha
- Dashboard de Status e Monitoramento (Ctrl+D)
- Monitor de Sistema (CPU, Memoria, Disco)
- Status dos provedores de IA em tempo real

#### v0.1.8-alpha
- Editor Markdown com Preview em tempo real
- Suporte a backlinks [[nota]]
- Sistema de Tags
- Graph View (mapa de conexoes)
- Integracao Multi-IA

---

## Roadmap

### Proximas Features
- [ ] Sincronizacao com nuvem
- [ ] Plugins/extensoes
- [ ] Busca avancada com filtros
- [ ] Exportacao para PDF
- [ ] Modo escuro

### Bugs Conhecidos
- Nenhum bug critico no momento

---

## Links
- **GitHub**: https://github.com/cfdmmarket-dot/Keepsidian
- **Projeto Pai**: CFDM AI OS TRIPLEX
