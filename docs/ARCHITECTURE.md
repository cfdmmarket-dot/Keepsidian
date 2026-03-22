# Keepsidian - Arquitetura do Codigo

## Estrutura de Arquivos
```
keepsidian/
├── keepsidian.py      # Aplicacao principal (monolitico)
├── README.md          # Documentacao publica
├── requirements.txt   # Dependencias Python
├── .gitignore         # Arquivos ignorados
└── docs/
    ├── DEVLOG.md      # Este arquivo - diario de desenvolvimento
    ├── ARCHITECTURE.md # Arquitetura do codigo
    └── FEATURES.md    # Lista de funcionalidades
```

---

## Classes Principais

### `KeypsidianMain` (QMainWindow)
Janela principal da aplicacao. Controla:
- Menu e toolbar
- Arvore de grupos (esquerda)
- Tabela de entradas (centro)
- Editor de notas (direita)
- Dashboard de status

**Atributos importantes:**
- `self.entries` - Lista de dicts com todas as entradas
- `self._kp_instance` - Instancia do PyKeePass (quando aberto .kdbx)
- `self.current_file` - Caminho do arquivo atual
- `self.vault_password` - Senha do vault (em memoria)
- `self.vault_keyfile` - Caminho do arquivo-chave

### `UnlockDialog` (QDialog)
Dialogo para desbloquear banco de dados.
- Suporta senha + arquivo-chave
- Usado ao abrir .kdbx existente

### `EntryDialog` (QDialog)
Dialogo para criar/editar entradas.
- Campos: titulo, usuario, senha, URL, notas, tags
- Tipos: Senha, Nota, Cartao, Documento, Identidade

### `ImportDialog` (QDialog)
Importacao de arquivos externos.
- Suporta: .kdbx, CSV, Bitwarden JSON
- Preview das entradas antes de importar

### `GraphViewDialog` (QDialog)
Visualizacao de conexoes entre notas.
- Mostra backlinks [[nota]]
- Grafo interativo

### `DashboardDialog` (QDialog)
Monitoramento do sistema.
- CPU, Memoria, Disco
- Status dos provedores de IA
- Estatisticas do vault

---

## Fluxo de Dados

### Abrir Banco .kdbx
```
Usuario seleciona arquivo
    ↓
UnlockDialog (pede senha/keyfile)
    ↓
PyKeePass abre arquivo
    ↓
Entradas carregadas em self.entries
    ↓
UI atualizada (arvore + tabela)
```

### Salvar Banco .kdbx
```
Usuario clica Salvar
    ↓
_save_kdbx() chamado
    ↓
Para cada entrada:
  - get_or_create_group() cria grupo se necessario
  - add_entry() ou atualiza existente
    ↓
kp.save() grava no disco
```

### Importar Entradas
```
ImportDialog aberto
    ↓
Usuario seleciona arquivo + formato
    ↓
import_kdbx() ou import_other_format()
    ↓
self.imported_entries populado
    ↓
finish_import() adiciona a self.entries
    ↓
UI atualizada
```

---

## Dependencias

### Obrigatorias
- **PyQt5**: Interface grafica
- **pykeepass**: Suporte a arquivos .kdbx

### Opcionais
- **markdown**: Preview de Markdown
- **requests**: Integracao com IAs cloud

---

## Padroes de Codigo

### Nomenclatura
- Metodos: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_CASE`

### Estrutura de Entrada (dict)
```python
{
    "type": "🔐 Senha",      # Tipo da entrada
    "title": "Titulo",       # Titulo
    "username": "user",      # Usuario
    "password": "pass",      # Senha
    "url": "https://...",    # URL
    "notes": "...",          # Notas (Markdown)
    "tags": "tag1, tag2",    # Tags separadas por virgula
    "group": "Pasta/Sub",    # Grupo/caminho
    "created": "2024-...",   # Data criacao
    "modified": "2024-..."   # Data modificacao
}
```

---

## Dicas para Contribuir

1. **Sempre atualizar VERSION** ao fazer mudancas
2. **Testar com .kdbx** antes de commitar
3. **Commit detalhado** com NOVIDADES e CORRECOES
4. **Push para GitHub** apos cada sessao
