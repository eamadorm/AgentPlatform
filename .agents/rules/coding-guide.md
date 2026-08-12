# Universal Engineering Standards

Follow these universal engineering standards for any code written in this repository:

## Core Principles
- **DRY & Simple**: Do not repeat logic. If a pattern appears three times, abstract it. Avoid overengineering; favor readability over "clever" code.
- **YAGNI (You Aren't Gonna Need It)**: Do not write code for hypothetical future use cases. Implement only what is required now.
- **Single Responsibility (SRP)**: Each class, module, and function must have one—and only one—reason to change.
- **OOP Principles**: Use Object-Oriented patterns to encapsulate state and behavior. Prefer **Composition over Inheritance**.
- **Dependency Injection**: Pass dependencies (like database clients or external services) into classes/functions rather than instantiating them internally. This ensures code is testable.

## Code Structure & Quality
- **Refactoring Rule**: Each function/method must not be greater than **50 lines** of code. If so, assess the possibility to split functionality into different functions following the Single Responsibility Principle.
- **Fail Fast**: Use "Guard Clauses" to return early. Avoid deeply nested `if/else` structures (The Arrow Anti-pattern).
- **No Magic Numbers/Strings**: Never hardcode numbers or strings in business logic. Extract them into descriptive Constants or Enums.
- **Side Effects**: Keep business logic "pure" by separating it from I/O (database, API calls, file system) whenever possible.
- **Typehints**: Always use typehints. Try to avoid general typehints such as `Any`.

## Repository Structure & Deployables
- **Service Isolation**: Each deployable service must be isolated in its respective top-level domain folder: `backend/<service>`, `frontend/<service>`, or `infra/<service>`.
- **Shared Naming**: If a feature spans multiple layers, the subfolder must have the EXACT SAME name across domains (e.g., `backend/auth` and `frontend/auth`).
- **Dependency Groups**: `pyproject.toml` (for backend) MUST be located at the top-level `backend/` directory. Dependencies must be organized into groups per service (e.g. using `uv add --group <service> <dependency>`). For the frontend, use **pnpm** exclusively to manage isolated dependencies per service.

## Business Logic Validation & Common Use Cases
- **Data Validation (Dual Enforcement)**: All core business rules MUST be enforced identically on both the **Frontend** (for immediate UX feedback) and the **Backend** (for strict data integrity and security).
- **Password Complexity**: Any password creation or reset flow must enforce the following strict criteria:
  - Minimum of 8 characters in length.
  - At least one uppercase letter and one lowercase letter.
  - At least one number.
  - At least one special character (e.g., `!@#$%^&*`).
  - Passwords and Confirmation Passwords MUST match exactly.
- **Sanitization**: All user inputs must be sanitized on the backend before database insertion to prevent SQL injection and XSS.

## Git Workflow (CRITICAL)
- **Branching**: Before creating ANY new branch for an issue, you MUST switch to the `main` branch and ensure it is fully up to date (`git checkout main && git pull`). ONLY then can you create the new branch from `main`. Do not branch off stale or unmerged branches.

## Naming & Documentation
- **Intent-Based Naming**: Use descriptive names for variables and functions. Avoid generic terms like `data`, `temp`, or `handle`. Names should reveal *why* the code exists.
- **Documentation (Docstrings & READMEs)**:
  - **README Mandate**: Each component, system, or subsystem must have its own `README.md` file. The README MUST include:
    - **In-depth behavior explanation**: What it does and the rationale/design decisions.
    - **Mermaid Diagrams**: Visualizing the component architecture, state machines, or workflow behavior.
    - **Usage & Setup**: Explicit instructions on how to set it up locally and how to use it.
    - **Make Commands**: ALL commands shown in the Usage or Setup sections MUST use `make` commands. Do NOT list direct `pnpm`, `npm`, or `uv` commands.
    - **Testing**: Clear instructions on how to run tests for the component.
  - **Classes**: Include at the top a brief description of what the class handles.
  - **Methods and Functions**: Must use the following structure:
    ```text
    2 or 3 lines describing what the function does

    Args:
        variable_name: type -> Description of the args

    Returns:
        type -> Description of the return
    ```

## Operations, Logging & Security
- **Logging Strategy**:
  - **INFO**: Log public method entries and major state changes.
  - **DEBUG**: Log internal logic, loops, and data transformations within private methods.
- **Actionable Error Messages**: Exceptions must include context (what failed, why, and relevant IDs). Avoid generic messages.
- **Configuration**: Never hardcode values. Use **Config Classes/Objects** to centralize environment variables and constants.
- **Secure by Design**: Never log PII (Personally Identifiable Information), tokens, or secrets. Always sanitize inputs.
- **Command Automation**: To execute a deployable, generate a Make command. For example, to login to gcloud, wrap the gcloud commands into a `make gcloud-auth` command; to execute a pipeline, wrap the necessary commands with a make command.
- **Lints**: Make sure that the code is always linted before making any commit.
- **Commits**: Use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`) for all version control changes.
