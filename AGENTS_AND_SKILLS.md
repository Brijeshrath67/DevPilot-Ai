# DevPilot AI Custom Agents & Skills

This document details the custom agents and skills implemented within the DevPilot AI platform.

## 1. Custom Skill: Security Scanner Skill (`SecuritySkill`)

- **File Path**: [security_skill.py](file:///e:/gdgkiit/backend/app/skills/security_skill.py)
- **Purpose**: Provides static code analysis scans across repository files to locate potential vulnerability patterns and credential disclosures.
- **Capabilities**:
  - **Secret Scans**: Utilizes regular expressions to flag exposed API Keys, JWT secrets, Bearer tokens, and AWS credential parameters.
  - **Unsafe Method Audits**: Scans for commands allowing execution of raw strings (e.g. `eval()`, `exec()`, `os.system()`).
  - **SQL Injection Risks**: Detects non-parameterized raw database executions where strings are concatenated or modulated directly.

---

## 2. Custom Agent: Security Audit Agent (`SecurityAgent`)

- **File Path**: [security_agent.py](file:///e:/gdgkiit/backend/app/agents/security_agent.py)
- **Purpose**: Consumes the `SecuritySkill` to execute full-repository security compliance audits.
- **Capabilities**:
  - **Dynamic Security Scoring**: Computes a dynamic security percentage starting at 100% and subtracting penalties for critical (-25%), high (-15%), and medium (-5%) issues.
  - **Health Metric Propagation**: Saves and merges computed scores into the project's centralized database health metrics history.
  - **Actionable Remediation Alerts**: Returns findings categorized by severity, line reference, specific file, and provides steps to resolve each issue.
