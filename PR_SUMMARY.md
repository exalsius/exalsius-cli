# PR Summary: Hexagonal Architecture Migration & Core Refactoring

## 🎯 Goal

This PR implements a comprehensive rewrite of the CLI application, migrating from a layered/module-based structure to a **Hexagonal Architecture (Ports & Adapters)**. This decoupling ensures business logic (`core`) is isolated from external concerns like the CLI UI and API Gateways (`adapters`), improving testability and maintainability.

## 🏗 Architectural Changes

The codebase has been reorganized into distinct domains (`auth`, `clusters`, `nodes`, `workspaces`, etc.), each following a strict internal structure:

- **Core (Inner Hexagon)**:
  - `core/domain.py`: Pure business entities and logic.
  - `core/ports/`: Interfaces (protocols) defining how the core interacts with the outside world (Gateways, Providers).
  - `core/service.py`: Application services orchestrating the domain logic.
- **Adapters (Outer Hexagon)**:
  - `adapters/gateway/`: Implementations of ports for external APIs (e.g., Auth0, Backend API).
  - `adapters/ui/`: CLI-specific implementations (Display logic, Interactive Flows).
  - `adapters/provider/`: Auxiliary adapters (e.g., SSH key providers).
  - `adapters/bundle.py`: Dependency injection bundles for wiring the application.
- **Composition Root**:
  - `app.py` (per module): Wires adapters to services and exposes the module's commands to the main CLI application.

## 📦 Key Domain Refactors

- **Clusters & Workspaces**: Major rewrite of `app.py` and `service.py` in these domains to support the new architecture. Configuration logic was moved to dedicated UI adapters (e.g., `workspaces/adapters/ui/configurators.py`).
- **Auth**: Migrated Auth0 and Keyring logic into `adapters/gateway`.
- **Nodes, Offers, Management, Services**: All aligned with the new directory structure, replacing flat `cli.py`/`service.py` files.

## 🛠 Shared Infrastructure & Improvements

- **IO Facade & UI Engine**: Introduced a sophisticated UI layer in `exls/shared/adapters/ui`:
  - **Flow Engine**: New `flow/` and `steps.py` to manage complex interactive user journeys (wizards) in a declarative way.
  - **Input/Output Facades**: Standardized `input/` and `output/` adapters to decouple the core from `typer`/`rich` direct calls.
  - **Rendering**: Centralized renderers for JSON, YAML, Table, and Text formats.
- **Core Utilities**:
  - `shared/core/parallel.py`: Added support for parallel execution.
  - `shared/core/polling.py`: Standardized polling mechanisms.
  - `shared/core/crypto.py`: Centralized cryptographic utilities.

## 📊 Stats

- **Files Changed**: 330
- **Lines**: +12,011 / -9,694
- **Dependencies**: Added `ruamel-yaml` and `cryptography`.

---

### Suggested Git Commit Message

```text
refactor: migrate cli to hexagonal architecture

- Reorganize all domains (clusters, workspaces, nodes, etc.) into core/adapters structure.
- Isolate business logic in core/service and core/domain.
- Implement Port interfaces for all external dependencies.
- Create shared IO Facade and Flow Engine for standardized UI interactions.
- Add bundled dependency injection in per-module app.py files.
- Remove legacy cli.py and monolithic service implementations.
```
