# Decision D001: Hub-Core MCP Architecture Refactoring

## Context

Análise completa do hub-core identificou múltiplos code smells e violações de padrões MCP:

**Problemas Críticos Identificados:**

1. **tools.py (2047 linhas)** - God Object
   - Arquivo massivo com todas as 8 ferramentas MCP
   - Viola Single Responsibility Principle
   - Funções auxiliares misturadas com lógica de ferramentas
   - Dificulta manutenção e testes

2. **brownfield.py (665 linhas)** - Classe Monolítica
   - RepositoryScanner, SliceGenerator, ContextExtractor em um arquivo
   - Responsabilidades misturadas (scan, slice, extract)
   - Difícil de testar unitariamente

3. **build_protocol.py (445 linhas)** - Gestão de Estado In-Memory
   - Dicionários in-memory para plans e approvals (_plans, _approvals)
   - Dados perdidos ao reiniciar servidor
   - Não persiste estado entre sessões

4. **learn_sync.py (514 linhas)** - Similar ao build_protocol
   - Estado in-memory para proposals (_proposals)
   - Sem persistência

5. **Falta de Separação de Concerns**
   - Lógica de negócio misturada com código MCP
   - Parsing de markdown repetido em múltiplos lugares
   - Validações duplicadas

6. **Ausência de Dependency Injection**
   - Componentes fortemente acoplados
   - Dificulta testes e mocking
   - _get_components_for_repo() é um workaround, não solução

7. **Falta de Abstrações**
   - Código de parsing markdown espalhado
   - Extração de dados repetida (status, title, etc.)
   - Sem interfaces/protocolos definidos

8. **Error Handling Inconsistente**
   - Alguns métodos retornam dict com 'error'
   - Outros lançam exceptions
   - Dificulta tratamento de erros pelo cliente

9. **Violação de FastMCP Best Practices**
   - Ferramentas com muita lógica interna
   - Estado mutável dentro do servidor
   - Falta de separação entre camadas (presentation/business/data)

## Decision

Refatorar hub-core seguindo arquitetura em camadas MCP:

**Nova Arquitetura (3 camadas):**

```
hub-core/
├── src/hub_core/
│   ├── domain/              # Camada de Domínio
│   │   ├── models/          # Dataclasses e Enums
│   │   │   ├── artifacts.py
│   │   │   ├── analysis.py
│   │   │   ├── build.py
│   │   │   └── learn.py
│   │   └── services/        # Lógica de Negócio
│   │       ├── intent_service.py
│   │       ├── analysis_service.py
│   │       ├── build_service.py
│   │       └── learn_service.py
│   │
│   ├── infrastructure/      # Camada de Infraestrutura
│   │   ├── persistence/     # File-based persistence
│   │   │   ├── file_store.py
│   │   │   ├── plan_repository.py
│   │   │   └── proposal_repository.py
│   │   ├── parsers/         # Markdown parsers
│   │   │   ├── markdown_parser.py
│   │   │   └── extractor.py
│   │   └── scanner/         # Brownfield scanning
│   │       ├── repo_scanner.py
│   │       ├── slice_generator.py
│   │       └── context_extractor.py
│   │
│   ├── mcp/                 # Camada MCP (Presentation)
│   │   ├── tools/           # Ferramentas MCP (thin layer)
│   │   │   ├── cm_init.py
│   │   │   ├── cm_intent.py
│   │   │   ├── cm_analyze.py
│   │   │   ├── cm_build.py
│   │   │   ├── cm_learn.py
│   │   │   ├── cm_validate.py
│   │   │   ├── cm_agent.py
│   │   │   └── cm_status.py
│   │   ├── server.py        # FastMCP server
│   │   └── decorators.py    # MCP helpers
│   │
│   └── shared/              # Código compartilhado
│       ├── config.py
│       ├── errors.py
│       └── utils.py
```

**Princípios da Refatoração:**

1. **Separation of Concerns**
   - Domain: Regras de negócio puras (testáveis sem I/O)
   - Infrastructure: I/O, parsers, persistence
   - MCP: Thin layer que conecta FastMCP aos services

2. **Dependency Injection**
   - Services recebem dependências via construtor
   - Facilita testes e substituição de implementações

3. **File-based Persistence**
   - Plans e Proposals salvos como JSON em `.context-mesh/`
   - Mantém repo-first approach
   - Permite versionamento com git

4. **Single Responsibility**
   - Cada módulo com responsabilidade clara
   - Tools MCP apenas mapeiam parâmetros para services

5. **Consistent Error Handling**
   - Services lançam exceptions customizadas
   - MCP layer captura e converte para dict responses

6. **Testability**
   - Domain services testáveis sem I/O
   - Mocks fáceis com DI
   - Testes unitários + integração separados

## Rationale

Esta refatoração resolve todos os code smells identificados:

- **God Object (tools.py)**: Dividido em 8 arquivos MCP + services
- **Classes Monolíticas**: Brownfield separado em 3 módulos
- **Estado In-Memory**: Substituído por file-based persistence
- **Acoplamento**: Resolvido com DI e interfaces
- **Parsing Repetido**: Centralizado em infrastructure/parsers
- **Error Handling**: Padronizado com custom exceptions
- **Testabilidade**: Domain services puros, facilmente testáveis

**Alinhamento com FastMCP Best Practices:**
- Tools são thin wrappers
- Lógica de negócio isolada
- Estado persistido, não in-memory
- Server stateless (dados em disco)

**Mantém Compatibilidade:**
- Interface MCP permanece igual
- Clientes não precisam mudar
- Apenas implementação interna muda

## Alternatives Considered

- **Refactoring Incremental Mínimo**: Apenas dividir tools.py em arquivos menores. Não resolve estado in-memory, acoplamento e falta de testes. Paliativo que não resolve problemas estruturais.
- **Migrar para Database (SQLite)**: Adiciona dependência externa, viola repo-first principle, complexidade desnecessária. File-based é suficiente para v1 e mantém simplicidade.
- **Microservices (múltiplos MCP servers)**: Over-engineering para escopo atual. Um servidor MCP bem estruturado é suficiente. Aumentaria complexidade operacional sem ganhos proporcionais.

## Consequences

### Positive
- Código 70% mais testável (domain services puros)
- Manutenção facilitada (responsabilidades claras)
- Onboarding mais rápido (arquitetura clara)
- Permite evolução (adicionar features sem quebrar)
- Debugging simplificado (camadas isoladas)
- Reutilização de código (services usáveis fora MCP)

### Trade-offs
- Inicialmente mais arquivos (mas melhor organização)
- Requer migração de código existente (~2-3 dias trabalho)
- Curva aprendizado para novos dev (mas arquitetura é padrão)
- File I/O adicional para persistence (mas negligível)

## Related

- Features: F004
- Decisions: D013, D014

## Status

- **Date**: 2026-03-03
- **Status**: Accepted
