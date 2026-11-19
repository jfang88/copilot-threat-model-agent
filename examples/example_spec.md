# Example input documents (fictional)

The worked example uses two fictional design documents. Page numbers are shown as [p.N].

## DOC1 - Document Intake & AI Summary Service - High-Level Design, v0.9, 2 Oct 2026 (24 pages)

**§3.1 Customer access [p.6]**
Customers sign in to the web portal and receive a session token valid for 24 hours. All uploads go through the API Gateway with WAF.

**§3.4 Document intake [p.7]**
The Intake Service accepts any file type up to 100 MB. Files are stored in Blob Storage under /cases/<case-number>/ and a job is posted to a Service Bus queue.

**§4.1 Summariser overview [p.9]**
The Summariser Agent is composed of four components (Table 4).

Table 4 - Summariser components [p.9]

| Component | Function |
|---|---|
| Text Extractor | Parses PDF, DOCX and images (OCR) into plain text |
| Prompt Builder | Assembles the prompt and retrieves context from the vector index |
| Agent Orchestrator | Calls the LLM and executes the tool calls it requests |
| Response Validator | Checks the summary against the JSON schema |

**§4.2 Text extraction [p.10]**
The Text Extractor runs in the same container as the Agent Orchestrator and uses open-source parsing libraries; OCR uses Tesseract.

**§4.3 Prompt construction and model access [p.11]**
The Prompt Builder concatenates the system prompt, document text and top-5 retrieved chunks into one prompt. The prompt and full document text are sent to the hosted LLM API using an API key stored in an environment variable. There is no limit on document length.

**§4.4 Agent tools [p.12]**
The Orchestrator exposes two tools to the model: search_cases (reads the Case DB) and update_case (writes case status and summary). Tool calls are executed with the service's database credentials. Conversation state is cached in Redis for 7 days.

**§4.5 Retrieval [p.13]**
Document chunks are embedded into a single shared vector index to support follow-up questions.

**§4.6 Review [p.14]**
The summary and case record are written to the Case DB. Staff reviewers sign in to the Review Portal with Entra ID SSO and approve the summary.

**§5.2 Storage layout [p.17]**
Blob paths use the sequential case number.

## DOC2 - Platform CI/CD Pipeline Design, v2.1, 15 Jul 2026 (12 pages)

**§2.1 Source control [p.4]**
Developers raise pull requests in GitHub. PR builds run on the shared self-hosted runners used for main-branch builds, with access to repository secrets.

**§2.3 Workflow dependencies [p.5]**
Workflows reference marketplace actions by tag.

**§3.1 Build [p.7]**
The build job builds container images and pushes them to Azure Container Registry using a service principal secret.

**§3.2 Deploy [p.8]**
The deploy job uses a cluster-admin kubeconfig stored as a repository secret to deploy to AKS. Image signatures are not verified at deployment.
