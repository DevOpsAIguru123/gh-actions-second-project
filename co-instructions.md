gotcha, Viinn — you want a GitHub Copilot instructions file that steers Copilot toward solid Terraform + Databricks cluster policies. here’s a drop-in you can commit as .github/copilot-instructions.md (VS Code, Visual Studio, JetBrains, web Copilot & code review all read this file).  ￼ ￼ ￼

note: VS Code also supports multiple scoped files in .github/instructions/*.instructions.md with applyTo frontmatter if you want per-folder rules.  ￼

⸻

.github/copilot-instructions.md

# Copilot: How to help on this repo

**Mission:** Generate and edit Terraform to manage Databricks **cluster policies** (interactive & job), keep infra consistent, safe, and cost-aware.

## Project context
- IaC: Terraform ≥ 1.5 using provider `databricks/databricks ~> 1.x`.
- Cloud: Azure Databricks (Unity Catalog enabled).
- Goals:
  1) Policy for **interactive** clusters (dev notebooks, small, SINGLE_USER).
  2) Policy for **job** clusters (autoscale, USER_ISOLATION, production tags).
  3) Optional sample clusters/jobs bound to those policies.
- Keep outputs minimal and modular; prefer variables for runtime, node types, and tags.

## What to generate (default behaviors)
- Use **policy families** as baselines:
  - `data "databricks_policy_family" "personal"` → interactive
  - `data "databricks_policy_family" "job"` → job
- Create:
  - `databricks_cluster_policy.interactive` with overrides:
    - `spark_version` (variable), `runtime_engine = "PHOTON"`,
    - `data_security_mode = "SINGLE_USER"`,
    - `autotermination_minutes` range (10–120, default 30),
    - `num_workers` range (0–4, default 1),
    - required tags `Project`, `Owner`.
  - `databricks_cluster_policy.job` with overrides:
    - `runtime_engine = "PHOTON"`,
    - autoscale min/max workers (2–6 default),
    - `data_security_mode = "USER_ISOLATION"`,
    - required tags `Project`, `Environment (dev|test|acc|prod)`, `Owner`.
- Provide **examples**:
  - An interactive cluster bound to `policy_id`.
  - A `databricks_job` task with `new_cluster.policy_id` set to the job policy.
- Add **permissions** so only allowed groups can `CAN_USE` each policy.

## Coding style & structure
- Layout:
  - `terraform/main.tf`, `variables.tf`, `outputs.tf`
  - `terraform/policies/*.tf` (or JSON inline via `definition = jsonencode({...})`)
  - `terraform/examples/cluster_interactive.tf`, `job_nightly_etl.tf`
- Naming:
  - Resources: `interactive`, `job`, suffix with environment if needed (e.g., `job_prod`).
  - Variables: `spark_version`, `node_type`, `default_autotermination`.
- Tags:
  - Always set `custom_tags = { Project, Owner, Environment }`.
- Versions:
  - Pin provider with `version = "~> 1.x"`. Avoid floating `latest`.

## Security & compliance (hard rules)
- **Never** commit secrets or tokens. Use `TF_VAR_databricks_host` / `TF_VAR_databricks_token` or OIDC.
- **Do not** suggest disabling security modes or widening network access.
- Prefer Photon, UC security modes, and auto-termination.
- If proposing init scripts or libraries, explain why and ensure they don’t bypass policies.

## Quality gates Copilot should add/check
- Include `terraform fmt`, `terraform validate`, and `tflint` guidance in PR text.
- Add example GitHub Actions workflow with:
  - `plan` on PR
  - `apply` on `main`
  - OIDC auth stub (no secrets in YAML)
- Embed comments explaining *why* each policy override exists.

## Common variables (prefer these when writing code)
```hcl
variable "databricks_host"  { type = string }
variable "databricks_token" { type = string, sensitive = true } # if not using OIDC
variable "spark_version"    { type = string, default = "14.3.x-scala2.12" }
variable "node_type"        { type = string, default = "Standard_DS3_v2" } # adjust per SKU
variable "env"              { type = string, default = "dev" }

Example snippets Copilot can reuse

Interactive policy (family + overrides)

data "databricks_policy_family" "personal" { name = "Personal Compute" }
resource "databricks_cluster_policy" "interactive" {
  name             = "Interactive - Guardrailed"
  policy_family_id = data.databricks_policy_family.personal.id
  definition = jsonencode({
    spark_version         = { type = "fixed", value = var.spark_version }
    node_type_id          = { type = "fixed", value = var.node_type }
    runtime_engine        = { type = "fixed", value = "PHOTON" }
    data_security_mode    = { type = "fixed", value = "SINGLE_USER" }
    autotermination_minutes = { type = "range", minValue = 10, maxValue = 120, defaultValue = 30 }
    num_workers           = { type = "range", minValue = 0, maxValue = 4, defaultValue = 1 }
    enable_elastic_disk   = { type = "fixed", value = true }
    custom_tags.Project   = { type = "required" }
    custom_tags.Owner     = { type = "required" }
  })
}

Job policy (family + overrides)

data "databricks_policy_family" "job" { name = "Job Compute" }
resource "databricks_cluster_policy" "job" {
  name             = "Jobs - Standardized"
  policy_family_id = data.databricks_policy_family.job.id
  definition = jsonencode({
    spark_version          = { type = "fixed", value = var.spark_version }
    runtime_engine         = { type = "fixed", value = "PHOTON" }
    node_type_id           = { type = "fixed", value = var.node_type }
    driver_node_type_id    = { type = "fixed", value = var.node_type }
    autotermination_minutes= { type = "fixed", value = 20 }
    data_security_mode     = { type = "fixed", value = "USER_ISOLATION" }
    enable_elastic_disk    = { type = "fixed", value = true }
    autoscale.min_workers  = { type = "range", minValue = 1, maxValue = 4, defaultValue = 2 }
    autoscale.max_workers  = { type = "range", minValue = 2, maxValue = 16, defaultValue = 6 }
    custom_tags.Project    = { type = "required" }
    custom_tags.Environment= { type = "allowed_values", values = ["dev","test","acc","prod"], defaultValue = var.env }
    custom_tags.Owner      = { type = "required" }
  })
}

Permissions

resource "databricks_permissions" "job_policy_use" {
  cluster_policy_id = databricks_cluster_policy.job.id
  access_control { group_name = "data-engineers"; permission_level = "CAN_USE" }
}
resource "databricks_permissions" "interactive_policy_use" {
  cluster_policy_id = databricks_cluster_policy.interactive.id
  access_control { group_name = "devs"; permission_level = "CAN_USE" }
}

Examples (for reference)

resource "databricks_cluster" "dev_notebook" {
  cluster_name  = "dev-notebook"
  policy_id     = databricks_cluster_policy.interactive.id
  spark_version = var.spark_version
  node_type_id  = var.node_type
  num_workers   = 1
  autotermination_minutes = 30
  single_user_name = "user@example.com"
  custom_tags = { Project = "playground", Owner = "user@example.com", Environment = var.env }
}

resource "databricks_job" "nightly_etl" {
  name = "nightly-etl"
  task {
    task_key = "ingest"
    new_cluster {
      policy_id     = databricks_cluster_policy.job.id
      spark_version = var.spark_version
      node_type_id  = var.node_type
      autoscale { min_workers = 2, max_workers = 6 }
      data_security_mode = "USER_ISOLATION"
    }
    notebook_task { notebook_path = "/Repos/etl/notebooks/01_ingest" }
  }
}

Pull request checklist (ask Copilot to include)
	•	✅ terraform fmt -check, terraform validate, tflint
	•	✅ Policy changes documented in README.md with rationale
	•	✅ No hardcoded secrets; CI uses OIDC or masked vars
	•	✅ Tags enforced (Project, Owner, Environment)

Anti-patterns (do NOT propose)
	•	❌ Disabling Photon or UC security modes
	•	❌ Removing auto-termination
	•	❌ Committing PATs or workspace URLs with tokens
	•	❌ Arbitrary node type upgrades without cost note

Good prompts to ask Copilot
	•	“Generate a cluster policy for interactive clusters using the Personal Compute family with SINGLE_USER and Photon, tagged and autoscaled constraints.”
	•	“Create a GitHub Actions workflow to plan on PR and apply on main using OIDC (no secrets).”
	•	“Add permissions so group data-engineers can use the job policy.”

---

### (Optional) Scoped instructions files (VS Code only)

If you want different rules per path, add files in `.github/instructions/*.instructions.md` and scope with `applyTo`.  [oai_citation:4‡GitHub Docs](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot?utm_source=chatgpt.com)

**`.github/instructions/terraform.instructions.md`**
```md
---
applyTo: "terraform/**/*.tf"
---

Prefer `jsonencode({...})` for policy `definition` blocks. Keep node types & spark versions in variables. Always enforce Photon and UC security modes.


⸻

want me to tailor the file to your exact env names (dev/test/acc/prod), node SKUs, or your CI (GitHub OIDC to Azure)? I can bake those conventions straight into the instructions so Copilot vibes perfectly with your stack.