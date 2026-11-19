---
title: "TM-02 Threat Library and Framework Selection"
subtitle: "Knowledge file for the Copilot DFD Threat Model agent - v1.0 (frameworks current as of November 2026)"
---

# TM-02 How to use this library

1. STRIDE per element is always applied (TM-01).
2. Use the selection triggers below to add framework lists. Apply every list whose trigger matches.
3. Cite framework IDs exactly as written in this file. Do not invent IDs or use older editions (for example A10:2021 SSRF is now part of A01:2025; LLM06:2025 Excessive Agency is now LLM03:2026).
4. CWE-### identifiers may be added for specific weaknesses when you are confident of the number. CAPEC, MITRE ATT&CK and MITRE ATLAS IDs are optional and only when confident.

# TM-02 Framework selection triggers

| Framework | Cite as | Apply when the spec mentions |
|---|---|---|
| STRIDE | S, T, R, I, D, E | Always |
| LINDDUN (privacy) | LINDDUN L / I / NR / DT / DD / U / NC | Personal data, customers, employees, identifiers, analytics, tracking, consent, GDPR, PDPO, PIPL, retention |
| OWASP Top 10:2025 (web apps) | A01:2025 .. A10:2025 | Web front ends, web services, server-side apps, frameworks, libraries |
| OWASP API Security Top 10:2023 | API1:2023 .. API10:2023 | REST, GraphQL, gRPC, gateways, partner/B2B APIs, mobile back ends, webhooks |
| OWASP Top 10 for LLM Applications 2026 | LLM01:2026 .. LLM10:2026 | LLMs, prompts, chatbots, copilots, RAG, embeddings, vector databases, fine-tuning, model APIs |
| OWASP Top 10 for Agentic Applications 2026 | ASI01 .. ASI10 | AI agents, tool or function calling, MCP servers, plugins, multi-agent workflows, agent memory, autonomous actions |
| OWASP Top 10 CI/CD Security Risks | CICD-SEC-1 .. CICD-SEC-10 | Source control, pipelines, build runners, artifact repositories, container registries, IaC, deployment, signing |
| CWE | CWE-### | Optional, specific weakness (for example CWE-798 hard-coded credentials, CWE-434 unrestricted upload, CWE-918 SSRF) |

# TM-02 STRIDE threat patterns

| STRIDE | Typical threats to look for | Typical controls |
|---|---|---|
| S Spoofing | Weak or missing authentication; shared accounts; static API keys; token theft or replay; service identity not verified (no mTLS); phishable MFA for admins; spoofed webhook or callback sender | SSO with phishing-resistant MFA, workload identity federation, mTLS, signed requests (HMAC/JWS), short-lived tokens bound to client |
| T Tampering | Unsigned artifacts or images; writable config; unvalidated input; message queue injection; parameter tampering; data modified at rest without integrity check; unpinned dependencies | Signing and verification (Sigstore, Notation), immutable storage, input validation, integrity hashes, pinned dependencies, admission control |
| R Repudiation | No audit log; logs writable by the actor; shared identities; AI agent actions not attributed to a user; missing timestamps | Append-only / immutable audit log, per-user and per-agent identities, signed log forwarding, retention policy |
| I Information disclosure | Data sent unencrypted; over-broad API responses; secrets in code or logs; cross-tenant data access; verbose errors; data sent to third parties; backups unprotected | TLS 1.2+, field-level encryption, response filtering, secret managers, tenant isolation enforced server-side, DLP, error handling that fails closed |
| D Denial of service | No rate limits; unbounded uploads or queries; expensive operations triggerable by anonymous users; single points of failure; cost exhaustion (cloud, LLM tokens) | Rate limiting and quotas, size limits, autoscaling with ceilings, circuit breakers, budget alerts |
| E Elevation of privilege | Missing authorisation checks; over-privileged service accounts; admin interfaces exposed; container breakout; IDOR; agents with broader tool rights than the user | Deny-by-default authorisation, least privilege, scoped tokens, separation of admin plane, PAM/JIT, sandboxing |

# TM-02 LINDDUN privacy threats

| Code | Category | Look for | Typical controls |
|---|---|---|---|
| L | Linking | Combining data sets or identifiers so records about the same person can be connected (shared IDs across services, analytics joins, cross-tenant indexes) | Pseudonymous per-context IDs, data minimisation, partitioned stores |
| I | Identifying | Learning who a person is from data thought to be anonymous (quasi-identifiers, free text, documents, metadata) | Anonymisation with re-identification testing, redaction, aggregation thresholds |
| NR | Non-repudiation | A person cannot deny an action when they should be able to (excessive logging of personal actions, permanent records) | Proportionate logging, retention limits, privacy-preserving logs |
| DT | Detecting | Inferring that a person is involved from observable side effects (different errors for existing accounts, timing, notifications) | Uniform responses, rate limiting, minimal metadata |
| DD | Data disclosure | Excessive collection, retention, processing or sharing of personal data, including to processors and AI services | Purpose limitation, retention schedule, DPA with processors, encryption, access control |
| U | Unawareness (and unintervenability) | Data subjects are not informed or cannot access, correct, object or delete | Privacy notices at the point of collection, data subject rights workflows, AI processing disclosure |
| NC | Non-compliance | Processing conflicts with law, policy or contract (residency, cross-border transfer, lawful basis, records of processing) | DPIA, data residency controls, transfer assessments, records of processing |

# TM-02 OWASP Top 10:2025 (web application risks)

| ID | Name | DFD cue |
|---|---|---|
| A01:2025 | Broken Access Control (includes SSRF) | Any process that takes an object ID or URL from a caller; admin functions; outbound fetches |
| A02:2025 | Security Misconfiguration | Default settings, exposed management ports, permissive CORS, cloud storage policies, debug modes |
| A03:2025 | Software Supply Chain Failures | Third-party libraries, base images, build tools, package registries, unsigned components |
| A04:2025 | Cryptographic Failures | Unencrypted flows or stores, weak algorithms, poor key management, missing certificate validation |
| A05:2025 | Injection | Untrusted input reaching interpreters: SQL, OS commands, templates, LDAP, NoSQL |
| A06:2025 | Insecure Design | Missing security requirements, business logic flaws, no threat model for critical flows |
| A07:2025 | Authentication Failures | Credential stuffing exposure, weak session handling, missing MFA, insecure recovery |
| A08:2025 | Software or Data Integrity Failures | Unsigned updates or artifacts, insecure deserialisation, untrusted CI/CD inputs |
| A09:2025 | Security Logging and Alerting Failures | No audit or security event logging, logs not monitored, no alerting |
| A10:2025 | Mishandling of Exceptional Conditions | Errors that fail open, leak data, or leave inconsistent state; unhandled parser failures |

# TM-02 OWASP API Security Top 10:2023

| ID | Name | DFD cue |
|---|---|---|
| API1:2023 | Broken Object Level Authorization | Endpoints taking object IDs without per-object ownership checks |
| API2:2023 | Broken Authentication | Weak token handling, missing authentication on some endpoints |
| API3:2023 | Broken Object Property Level Authorization | Responses exposing extra fields; mass assignment on updates |
| API4:2023 | Unrestricted Resource Consumption | No limits on size, rate, pagination or costly operations |
| API5:2023 | Broken Function Level Authorization | Admin or privileged functions callable by ordinary users |
| API6:2023 | Unrestricted Access to Sensitive Business Flows | Automatable flows (purchase, sign-up, payment) without abuse controls |
| API7:2023 | Server Side Request Forgery | API fetches a caller-supplied URL |
| API8:2023 | Security Misconfiguration | Gateway, CORS, TLS, headers, verbose errors |
| API9:2023 | Improper Inventory Management | Undocumented, old or shadow API versions and hosts |
| API10:2023 | Unsafe Consumption of APIs | Trusting third-party API responses without validation |

# TM-02 OWASP Top 10 for LLM Applications 2026

| ID | Name | DFD cue |
|---|---|---|
| LLM01:2026 | Prompt Injection | Any untrusted text, document, image, audio, web page, email or memory that reaches the model (direct and indirect) |
| LLM02:2026 | Sensitive Information Disclosure | Personal or confidential data in prompts, context, outputs, logs, embeddings or sent to a model provider |
| LLM03:2026 | Excessive Agency | Model has more tools, permissions or autonomy than its task needs |
| LLM04:2026 | Supply Chain | Third-party models, model hubs, adapters, datasets, model APIs |
| LLM05:2026 | Data and Model Poisoning | Training, fine-tuning or retrieval data that an attacker can influence |
| LLM06:2026 | Unbounded Consumption | No limits on tokens, requests, document size or cost |
| LLM07:2026 | Misinformation | Users or processes act on model output without verification |
| LLM08:2026 | Hidden Context Exposure | System prompts, instructions, tool definitions or hidden context that can be extracted (formerly System Prompt Leakage) |
| LLM09:2026 | Vector and Embedding Weaknesses | Shared or unpartitioned vector stores, embedding inversion, retrieval access control |
| LLM10:2026 | Improper Output Handling | Model output passed to browsers, shells, SQL, APIs or other systems without validation or encoding |

# TM-02 OWASP Top 10 for Agentic Applications 2026

| ID | Name | DFD cue |
|---|---|---|
| ASI01 | Agent Goal Hijack | Injected content in inputs, documents or tool results redirects the agent's objective or plan |
| ASI02 | Tool Misuse and Exploitation | Agent uses an authorised tool unsafely (wrong parameters, destructive actions, data exfiltration via tools) |
| ASI03 | Identity and Privilege Abuse | Agent uses delegated, inherited or cached credentials beyond what the requesting user should have |
| ASI04 | Agentic Supply Chain Vulnerabilities | Malicious or tampered models, tools, prompts, plugins or MCP servers loaded at runtime |
| ASI05 | Unexpected Code Execution (RCE) | Agent generates or runs code, or tool use leads to code running on a host or container |
| ASI06 | Memory and Context Poisoning | Persistent memory, summaries, embeddings or retrieval stores that an attacker can write to |
| ASI07 | Insecure Inter-Agent Communication | Agent-to-agent messages without authentication, integrity or replay protection |
| ASI08 | Cascading Failures | One faulty agent or tool output propagates through multi-step or multi-agent workflows |
| ASI09 | Human-Agent Trust Exploitation | Humans approve agent actions or outputs they cannot verify; persuasive or misleading agent output |
| ASI10 | Rogue Agents | Compromised or misaligned agent acting outside its intended function while appearing legitimate |

Design principle for agentic systems: least agency. Every tool, permission and degree of autonomy the agent does not need is attack surface.

# TM-02 OWASP Top 10 CI/CD Security Risks

| ID | Name | DFD cue |
|---|---|---|
| CICD-SEC-1 | Insufficient Flow Control Mechanisms | One identity can push code or artifacts to production without independent review or approval |
| CICD-SEC-2 | Inadequate Identity and Access Management | Over-privileged, shared, stale or external identities in SCM, CI or registries |
| CICD-SEC-3 | Dependency Chain Abuse | Dependency confusion, typosquatting, unpinned or unverified packages |
| CICD-SEC-4 | Poisoned Pipeline Execution (PPE) | Untrusted code (PRs, forks, branches) can change what the pipeline executes |
| CICD-SEC-5 | Insufficient PBAC (Pipeline-Based Access Controls) | Pipeline jobs have more access to secrets, systems or environments than their task needs |
| CICD-SEC-6 | Insufficient Credential Hygiene | Static, long-lived or exposed secrets in pipelines, code, images or logs |
| CICD-SEC-7 | Insecure System Configuration | Weak configuration of SCM, CI servers, runners, registries |
| CICD-SEC-8 | Ungoverned Usage of 3rd Party Services | Third-party apps, actions or integrations with access to code or pipelines |
| CICD-SEC-9 | Improper Artifact Integrity Validation | Artifacts or images deployed without signature or provenance verification |
| CICD-SEC-10 | Insufficient Logging and Visibility | No audit trail for pipeline, SCM or registry activity |

# TM-02 Supporting references (cite only when confident)

- CWE: weakness IDs, for example CWE-79, CWE-89, CWE-200, CWE-285, CWE-306, CWE-311, CWE-434, CWE-502, CWE-798, CWE-918.
- CAPEC: attack patterns for describing how a threat is executed.
- MITRE ATT&CK: adversary techniques, useful for detection controls.
- MITRE ATLAS: adversary techniques against AI systems; pair with LLM and ASI IDs.
- SLSA: supply chain build levels; use when recommending provenance controls for CICD-SEC-9 and A03:2025.
- OWASP ASVS: use to phrase testable control requirements.
- OWASP MCP Top 10: exists for MCP tool servers; do not cite its IDs (not in this library) - use ASI02, ASI04 or ASI07 instead.

# TM-02 Common mappings (for consistency)

| Situation in the spec | Cite |
|---|---|
| Static API key or password on a flow | S; A07:2025; CICD-SEC-6 if in a pipeline; CWE-798 if hard-coded |
| Object ID taken from caller | E or I; A01:2025; API1:2023 |
| File upload processed by a parser | T; A05:2025 or A10:2025; CWE-434 |
| Personal data sent to a third-party AI provider | I; LLM02:2026; LINDDUN DD; LINDDUN NC if cross-border |
| Untrusted document or web content read by an LLM or agent | E or T; LLM01:2026; ASI01 |
| Agent with write access to business systems | E; LLM03:2026; ASI02; ASI03 |
| Shared vector index across tenants | I; LLM09:2026; LINDDUN L |
| Model output written to DB, HTML, shell or API | T; LLM10:2026; A05:2025 |
| PR builds with secrets / unpinned actions | T; CICD-SEC-4; CICD-SEC-3; A03:2025 |
| Deploy without signature verification | T; CICD-SEC-9; A08:2025 |
| No audit log for admin or AI actions | R; A09:2025; CICD-SEC-10 for pipelines |
| No rate limit or size limit | D; API4:2023; LLM06:2026 for model calls |
| Error path fails open | E or I; A10:2025 |
