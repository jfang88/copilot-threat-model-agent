# Document Intake & AI Summary Service - spec v0.9 (fictional example)

- §3.1 Customers sign in to the web portal and receive a session token. Uploads go through the API Gateway with WAF.
- §3.4 The Intake Service accepts any file type up to 100 MB, stores it in Blob Storage under /cases/<case-number>/ and puts a job on a queue.
- §4.2 The Summariser Agent reads the document, extracts text and builds a prompt.
- §4.3 The prompt and full document text are sent to a hosted LLM API using an API key. No limit on document length.
- §4.4 Chunks are embedded into a single shared vector index to support follow-up questions.
- §4.5 The summary and case record are written to the Case DB. Staff reviewers sign in to the Review Portal with Entra ID SSO and approve the summary.
- §5.2 Blob paths use the sequential case number.
- §6.1 Developers raise PRs to GitHub; GitHub Actions builds images and deploys to AKS using a cluster-admin token stored as a repository secret. PR builds run on the same runners. Marketplace actions are referenced by tag.
