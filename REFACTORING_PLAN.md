# Hub-Core Refactoring Plan

> **Baseado em**: Decision D001 - Hub-Core MCP Architecture Refactoring
> **Data**: 2026-03-03
> **Status**: Planejamento

---

## 📊 Análise de Code Smells

### Resumo Executivo

| Arquivo | Linhas | Problemas Principais | Severidade |
|---------|--------|---------------------|------------|
| `tools.py` | 2047 | God Object, SRP violation, coupling | 🔴 Crítico |
| `brownfield.py` | 665 | Monolithic class, responsibilities mixing | 🟡 Alto |
| `build_protocol.py` | 445 | In-memory state, no persistence | 🟡 Alto |
| `learn_sync.py` | 514 | In-memory state, no persistence | 🟡 Alto |
| `bundler.py` | 298 | Parsing duplication | 🟢 Médio |
| `loader.py` | 244 | Acceptable | ✅ OK |
| `validator.py` | 280 | Acceptable | ✅ OK |

**Total de Linhas**: 5,034 (5k)  
**Linhas com Problemas**: ~3,671 (73%)

---

## 🎯 Objetivos da Refatoração

### Técnicos
1. ✅ Separar concerns (Domain/Infrastructure/MCP)
2. ✅ Implementar Dependency Injection
3. ✅ Adicionar file-based persistence
4. ✅ Padronizar error handling
5. ✅ Melhorar testabilidade (70%+ coverage target)

### Não-Funcionais
- Manter compatibilidade MCP (zero breaking changes)
- Reduzir tempo de onboarding (arquitetura clara)
- Facilitar debugging (camadas isoladas)
- Permitir evolução incremental

---

## 🏗️ Nova Arquitetura

```
hub-core/
├── src/hub_core/
│   ├── domain/              # 🧠 Business Logic (Pure Python, No I/O)
│   │   ├── models/          # Dataclasses e Enums
│   │   │   ├── __init__.py
│   │   │   ├── artifacts.py      # Feature, Decision, Pattern models
│   │   │   ├── analysis.py       # StructuralAnalysis, SliceDefinition
│   │   │   ├── build.py          # BuildPlan, ApprovalState, ExecutionInstruction
│   │   │   └── learn.py          # LearningProposal, OutcomeSummary
│   │   │
│   │   └── services/        # Business Rules (Testable, DI-ready)
│   │       ├── __init__.py
│   │       ├── intent_service.py     # Feature/Decision/Agent CRUD
│   │       ├── analysis_service.py   # Brownfield analysis orchestration
│   │       ├── build_service.py      # Plan/Approve/Execute workflow
│   │       └── learn_service.py      # Learn Sync workflow
│   │
│   ├── infrastructure/      # 🔧 External Interactions (I/O, Parsing, Scanning)
│   │   ├── persistence/     # File-based storage
│   │   │   ├── __init__.py
│   │   │   ├── file_store.py         # Generic JSON read/write
│   │   │   ├── plan_repository.py    # BuildPlan persistence
│   │   │   └── proposal_repository.py # LearningProposal persistence
│   │   │
│   │   ├── parsers/         # Markdown parsing
│   │   │   ├── __init__.py
│   │   │   ├── markdown_parser.py    # Extract sections, status, title
│   │   │   └── extractor.py          # Extract AC, constraints, links
│   │   │
│   │   └── scanner/         # Brownfield scanning
│   │       ├── __init__.py
│   │       ├── repo_scanner.py       # Language/framework detection
│   │       ├── slice_generator.py    # Repository slicing
│   │       └── context_extractor.py  # Artifact extraction
│   │
│   ├── mcp/                 # 🎨 MCP Presentation Layer (Thin Wrappers)
│   │   ├── tools/           # MCP tool definitions (8 tools)
│   │   │   ├── __init__.py
│   │   │   ├── cm_init.py            # new/existing/migrate
│   │   │   ├── cm_intent.py          # CRUD features/decisions/bugs
│   │   │   ├── cm_analyze.py         # scan/slice/extract/report
│   │   │   ├── cm_build.py           # bundle/plan/approve/execute
│   │   │   ├── cm_learn.py           # initiate/review/accept/apply
│   │   │   ├── cm_validate.py        # validation logic
│   │   │   ├── cm_agent.py           # agent CRUD
│   │   │   └── cm_status.py          # project status
│   │   │
│   │   ├── server.py        # FastMCP server setup
│   │   └── decorators.py    # MCP helpers (error handling, etc.)
│   │
│   └── shared/              # 🔁 Cross-cutting concerns
│       ├── __init__.py
│       ├── config.py         # Configuration (paths, constants)
│       ├── errors.py         # Custom exceptions
│       └── utils.py          # Helper functions
│
├── tests/                   # 🧪 Test suite
│   ├── unit/
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── integration/
│   └── fixtures/
│
├── pyproject.toml
└── README.md
```

---

## 📋 Plano de Execução (Faseado)

### **Fase 1: Fundação** (Dia 1-2) 🏗️

**Objetivo**: Criar estrutura base sem quebrar código existente

**Tarefas**:
1. ✅ Criar estrutura de diretórios (`domain/`, `infrastructure/`, `mcp/`, `shared/`)
2. ✅ Implementar `shared/errors.py` com custom exceptions:
   ```python
   class ContextMeshError(Exception): pass
   class ArtifactNotFoundError(ContextMeshError): pass
   class ValidationError(ContextMeshError): pass
   class PersistenceError(ContextMeshError): pass
   ```
3. ✅ Implementar `shared/config.py` com configurações globais
4. ✅ Mover dataclasses para `domain/models/`:
   - `artifacts.py` (de loader.py, bundler.py)
   - `analysis.py` (de brownfield.py)
   - `build.py` (de build_protocol.py)
   - `learn.py` (de learn_sync.py)

**DoD Fase 1**:
- [ ] Estrutura de pastas criada
- [ ] Models importáveis sem erros
- [ ] Custom exceptions definidas
- [ ] Config centralizado
- [ ] Imports ajustados (código antigo ainda funciona)

---

### **Fase 2: Infrastructure** (Dia 3-4) 🔧

**Objetivo**: Implementar camada de infraestrutura (parsers, persistence, scanner)

**Tarefas**:

#### 2.1 Parsers (refatorar parsing espalhado)
```python
# infrastructure/parsers/markdown_parser.py
class MarkdownParser:
    @staticmethod
    def extract_title(content: str) -> str: ...
    @staticmethod
    def extract_status(content: str) -> str: ...
    @staticmethod
    def extract_section(content: str, section: str) -> str: ...
```

#### 2.2 File Persistence
```python
# infrastructure/persistence/file_store.py
class FileStore:
    def __init__(self, base_path: Path): ...
    def save(self, key: str, data: dict) -> None: ...
    def load(self, key: str) -> dict: ...
    def exists(self, key: str) -> bool: ...
    def delete(self, key: str) -> None: ...

# infrastructure/persistence/plan_repository.py
class PlanRepository:
    def __init__(self, store: FileStore): ...
    def save_plan(self, plan: BuildPlan) -> None: ...
    def load_plan(self, plan_id: str) -> Optional[BuildPlan]: ...
    def list_plans(self) -> List[BuildPlan]: ...
```

#### 2.3 Scanner (refatorar brownfield.py)
- Dividir em 3 módulos:
  - `repo_scanner.py` (RepositoryScanner)
  - `slice_generator.py` (SliceGenerator)
  - `context_extractor.py` (ContextExtractor)

**DoD Fase 2**:
- [ ] MarkdownParser com testes unitários
- [ ] FileStore com testes de I/O
- [ ] PlanRepository e ProposalRepository funcionais
- [ ] Scanner modularizado e testável
- [ ] Código antigo ainda funciona (dupla implementação temporária)

---

### **Fase 3: Domain Services** (Dia 5-6) 🧠

**Objetivo**: Extrair lógica de negócio para services puros

**Tarefas**:

#### 3.1 IntentService
```python
# domain/services/intent_service.py
class IntentService:
    def __init__(self, loader: ContextLoader, parser: MarkdownParser):
        self.loader = loader
        self.parser = parser
    
    def create_feature(self, content: dict) -> Feature: ...
    def get_feature(self, name: str) -> Feature: ...
    def update_feature(self, name: str, updates: dict) -> Feature: ...
    def list_features(self) -> List[Feature]: ...
```

#### 3.2 BuildService
```python
# domain/services/build_service.py
class BuildService:
    def __init__(
        self,
        loader: ContextLoader,
        plan_repo: PlanRepository,
        parser: MarkdownParser
    ):
        ...
    
    def create_plan(self, feature_name: str) -> BuildPlan: ...
    def approve_plan(self, plan_id: str, action: str) -> ApprovalState: ...
    def generate_instructions(self, plan_id: str) -> List[ExecutionInstruction]: ...
```

#### 3.3 AnalysisService
```python
# domain/services/analysis_service.py
class AnalysisService:
    def __init__(
        self,
        scanner: RepoScanner,
        slice_gen: SliceGenerator,
        extractor: ContextExtractor
    ):
        ...
    
    def scan(self) -> StructuralAnalysis: ...
    def generate_slices(self, strategy: str) -> List[SliceDefinition]: ...
    def extract_artifacts(self, slice_id: str) -> List[ProposedArtifact]: ...
```

#### 3.4 LearnService
```python
# domain/services/learn_service.py
class LearnService:
    def __init__(
        self,
        loader: ContextLoader,
        proposal_repo: ProposalRepository
    ):
        ...
    
    def initiate_learn_sync(self, feature_name: str, ...) -> LearningProposal: ...
    def get_proposal(self, proposal_id: str) -> LearningProposal: ...
    def apply_learnings(self, proposal_id: str, ...) -> dict: ...
```

**DoD Fase 3**:
- [ ] Services implementados com DI
- [ ] Testes unitários (mocks para I/O)
- [ ] 70%+ coverage nos services
- [ ] Services reutilizáveis fora de MCP

---

### **Fase 4: MCP Layer** (Dia 7-8) 🎨

**Objetivo**: Refatorar tools.py em 8 arquivos thin wrappers

**Tarefas**:

1. ✅ Dividir `tools.py` (2047 linhas) em:
   - `mcp/tools/cm_init.py` (~250 linhas)
   - `mcp/tools/cm_intent.py` (~300 linhas)
   - `mcp/tools/cm_analyze.py` (~250 linhas)
   - `mcp/tools/cm_build.py` (~200 linhas)
   - `mcp/tools/cm_learn.py` (~200 linhas)
   - `mcp/tools/cm_validate.py` (~100 linhas)
   - `mcp/tools/cm_agent.py` (~150 linhas)
   - `mcp/tools/cm_status.py` (~150 linhas)

2. ✅ Implementar `mcp/decorators.py` para error handling:
   ```python
   def handle_mcp_errors(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           try:
               return func(*args, **kwargs)
           except ContextMeshError as e:
               return {"error": str(e), "type": type(e).__name__}
           except Exception as e:
               return {"error": f"Internal error: {str(e)}"}
       return wrapper
   ```

3. ✅ Refatorar `server.py` para injetar services:
   ```python
   def create_server(repo_root: Optional[Path] = None) -> FastMCP:
       mcp = FastMCP("Hub Core")
       
       # Setup dependencies
       loader = ContextLoader(repo_root or Path.cwd())
       parser = MarkdownParser()
       store = FileStore(repo_root / ".context-mesh")
       plan_repo = PlanRepository(store)
       
       # Setup services
       intent_service = IntentService(loader, parser)
       build_service = BuildService(loader, plan_repo, parser)
       
       # Register tools with DI
       register_cm_init(mcp, loader, parser)
       register_cm_intent(mcp, intent_service)
       register_cm_build(mcp, build_service)
       ...
       
       return mcp
   ```

**DoD Fase 4**:
- [ ] 8 arquivos MCP criados (thin wrappers)
- [ ] Decorators para error handling
- [ ] Server.py com DI setup
- [ ] Todos os testes MCP passando
- [ ] Interface MCP inalterada (compatibilidade)

---

### **Fase 5: Migração e Cleanup** (Dia 9) 🧹

**Objetivo**: Remover código antigo e finalizar migração

**Tarefas**:
1. ✅ Remover arquivos antigos:
   - `tools.py` → deletar (substituído por mcp/tools/)
   - `brownfield.py` → deletar (substituído por infrastructure/scanner/)
   - `build_protocol.py` → deletar (substituído por domain/services/build_service.py)
   - `learn_sync.py` → deletar (substituído por domain/services/learn_service.py)

2. ✅ Atualizar imports em:
   - `server.py`
   - `__init__.py`
   - Testes

3. ✅ Adicionar persistence para plans/proposals:
   - Criar `.context-mesh/plans/` ao inicializar
   - Criar `.context-mesh/proposals/`
   - Adicionar `.gitignore` para temporários

4. ✅ Documentação:
   - Atualizar `README.md` com nova arquitetura
   - Adicionar `ARCHITECTURE.md` explicando camadas
   - Atualizar docstrings

**DoD Fase 5**:
- [ ] Código antigo removido
- [ ] Imports ajustados
- [ ] Persistence configurada
- [ ] Documentação atualizada
- [ ] Git history preservado

---

### **Fase 6: Testes e Validação** (Dia 10) 🧪

**Objetivo**: Garantir qualidade e cobertura

**Tarefas**:

1. ✅ Testes Unitários (domain/services):
   ```python
   # tests/unit/domain/services/test_intent_service.py
   def test_create_feature_success(mock_loader, mock_parser):
       service = IntentService(mock_loader, mock_parser)
       feature = service.create_feature({"title": "Test", ...})
       assert feature.title == "Test"
   ```

2. ✅ Testes Integração (infrastructure):
   ```python
   # tests/integration/test_plan_persistence.py
   def test_save_and_load_plan(tmp_path):
       store = FileStore(tmp_path)
       repo = PlanRepository(store)
       plan = BuildPlan(...)
       repo.save_plan(plan)
       loaded = repo.load_plan(plan.plan_id)
       assert loaded == plan
   ```

3. ✅ Testes E2E (mcp):
   ```python
   # tests/integration/test_mcp_workflow.py
   def test_full_build_workflow(server):
       # Create feature via cm_intent
       result = server.call_tool("cm_intent", {...})
       # Create plan via cm_build
       plan = server.call_tool("cm_build", {"action": "plan", ...})
       # Approve plan
       approval = server.call_tool("cm_build", {"action": "approve", ...})
       assert approval["status"] == "approved"
   ```

4. ✅ Coverage target: 70%+

**DoD Fase 6**:
- [ ] 70%+ test coverage
- [ ] Testes unitários passando
- [ ] Testes integração passando
- [ ] Testes E2E passando
- [ ] CI configurado (GitHub Actions)

---

## 📈 Métricas de Sucesso

| Métrica | Antes | Meta | Como Medir |
|---------|-------|------|------------|
| **Linhas por arquivo** | 2047 (tools.py) | <300 | `wc -l src/**/*.py` |
| **Test Coverage** | ~10% | 70%+ | `pytest --cov` |
| **Cyclomatic Complexity** | Alto | <10/função | `radon cc` |
| **Acoplamento** | Alto | Baixo (DI) | Análise manual |
| **Bugs reportados** | N/A | 0 após refactor | GitHub Issues |

---

## 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Breaking changes em MCP | 🟡 Médio | 🔴 Alto | Manter interface MCP inalterada, testes E2E |
| Perda de dados (plans/proposals) | 🟢 Baixo | 🔴 Alto | Implementar persistence antes de remover in-memory |
| Tempo de migração > estimado | 🟡 Médio | 🟡 Médio | Faseamento permite entregar valor incremental |
| Regressões não detectadas | 🟡 Médio | 🔴 Alto | 70%+ test coverage, testes E2E |

---

## 📚 Referências

- **Decision D001**: Hub-Core MCP Architecture Refactoring
- **Decision D013**: MCP Simplification (8 tools consolidados)
- **Decision D014**: Brownfield Extraction Artifact Classification
- **FastMCP Best Practices**: https://github.com/jlowin/fastmcp
- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans

---

## 🎯 Próximos Passos

1. ✅ Aprovar Decision D001
2. ✅ Criar branch `refactor/hub-core-architecture`
3. ✅ Iniciar Fase 1 (Fundação)
4. ⏸️ Review incremental após cada fase
5. ⏸️ Merge após Fase 6 completa

---

**Última atualização**: 2026-03-03  
**Responsável**: Equipe Hub-Core  
**Status**: 📝 Aprovado para execução
