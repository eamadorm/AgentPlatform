# Altea Development Rules & Architecture Constraints

## 1. Technology Stack
- **Backend:** Python (FastAPI)
- **Frontend:** Next.js (React) with Prettier/ESLint for formatting.
- **Database:** PostgreSQL with `pgvector` extension.
- **CI/CD & Cloud:** Google Cloud Platform (GCP) and Google CloudBuild.
- **Testing:** `pytest` and `pytest-bdd` (linking to existing Gherkin `.feature` files).

## 2. GitHub & CLI Usage
- **Git/GitHub Operations:** Whenever creating issues, milestones, PRs, commits, and other related operations, you MUST use the `git` or `gh` CLI directly as required.
- **Makefile Orchestration:** Use the root `Makefile` for core operations (e.g., `make gcloud-login`, `make gh-login`, `make db-up`, `make db-down`). Additionally, **each module MUST define its own make commands** specifically for testing and running that module locally.
- **Workstream Representation (GitHub):** Workstreams (e.g., Backend, Frontend, Infra) MUST be explicitly represented in GitHub. This is achieved by:
  1. **Labels:** Applying strict labels to all Issues and PRs (e.g., `backend`, `frontend`, `infra`).
  2. **Branch Naming:** Prefixing all branch names with the workstream identifier (e.g., `backend/feat-auth`, `infra/setup-db`, `frontend/fix-ui`) to clearly separate development tracks within the monorepo.
- **Project Management (Milestones & Issues):** 
  - **Milestone First:** Before developing anything, a GitHub Milestone MUST be created with a brief description of what we are trying to achieve. The Milestone itself MUST be aligned to a specific workstream.
  - **Assignment:** Every Pull Request (PR) and GitHub Issue MUST be strictly assigned to an active Milestone.
  - **Issue Naming:** Issues logically belonging to a Milestone MUST be sequentially numbered in their title using the format: `[MilestoneName] - [Number] - [Specific Name of the issue]` (e.g., `AuthSetup - 01 - Create JWT Middleware`).
  - **Issue Formatting (Spec-Driven Development):** Every GitHub issue created MUST adhere strictly to Spec-Driven Development principles and use the following exact template for its body:
    ```
    As a developer,
    I want to...
    So that...
    
    ## Acceptance Criteria
    
    ## Definition of Done
    
    ## Considerations
    ```

## 3. Development Workflow (Local First & Cloud Testing)
- **Local Verification:** All development must be rigorously verified locally before pushing to remote or establishing final deployment infrastructure.
- **Temporal Cloud Resources:** If a feature requires testing directly in the cloud during the development phase, you must create `create_temp_resources.sh` and `delete_temp_resources.sh` scripts in the root directory. These scripts allow for rapid provisioning and teardown of temporary cloud testing environments.
- **Do Not Commit Temp Scripts:** Ensure `create_temp_resources.sh` and `delete_temp_resources.sh` remain uncommitted (they are already ignored via `.gitignore`).
- **Main Branch Protection:** Direct commits to the `main` branch are strictly PROHIBITED. All development must occur on separate feature branches. The `main` branch can only be updated via Pull Requests (PRs).
- **Merge & CI/CD Strategy:** Only merge PRs into `main` after local (and temporary cloud) verification succeeds. Formal CI/CD resources (CloudBuild YAMLs) and final deployments should only be created and pushed after this verification.

## 4. Infrastructure Isolation
- **Infrastructure as Code (IaC):** There MUST be an `infrastructure/` folder dedicated to each workstream or architectural "unit" (e.g., `backend/infrastructure/`, `frontend/infrastructure/`). This guarantees a clean division of deployments and cloud resources per component.

## 5. Directory Structure & Documentation
- **Just-In-Time (JIT) Creation:** Do NOT create massive scaffolding or template folders upfront. Only create new folders, files, or services at the exact moment they are needed by a specific feature development to keep PRs clean and focused.
- **Mandatory READMEs:** For each new module or domain developed, there MUST be a `README.md` included in that module's root directory containing a general description of what the module does, so any developer (or agent) is immediately aware of its purpose.
- **Advanced Documentation (`docs/`):** Any documentation or specifications that do not fit into a standard `README.md` (e.g., highly technical processes, overarching system architecture, or BDD feature specs) MUST be defined in the root `docs/` directory. These subfolders MUST be sequentially numbered logically based on the topic (e.g., `01-features`, `02-specifications`, `03-architecture`). The core purpose of this numbering is to intuitively guide the user on where to start and what to read next.

## 6. Pre-Commit Hooks & Quality Gates
- **Mandatory Pre-Commit:** All commits must be compliant with `pre-commit` hooks (e.g., linting, formatting, security checks).
- **No Bypassing:** You must NEVER use the `--no-verify` flag (or equivalent) to bypass pre-commit hooks during `git commit`.

## 7. Infrastructure as Code (Terraform)
- **Terraform First:** Whenever possible, all cloud resources MUST be managed through Terraform. 
- **Complex CD Logic:** If a deployment step involves complex logic that Terraform cannot handle effectively during Continuous Deployment (CD), encapsulate that logic within a dedicated `.sh` script rather than writing complex inline CLI commands in the pipeline definition.

## 8. Scope Discipline
- **Strict Scope Execution:** The agent MUST ONLY modify code, files, or configurations that have been explicitly requested by the user. Do NOT proactively refactor, rename, or alter unrelated code under the justification of "since I am already here, I will change...". Stick strictly to the requested scope.
