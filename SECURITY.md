# Security Policy

This repository should not contain credentials, private dataset mirrors, model
weights, API keys, or machine-specific absolute paths.

If you find sensitive material in a public copy of this artifact, report it
through the review system or repository issue tracker. Do not post secrets in a
public issue body.

The optional LLM adapter is disabled by default and uses fail-closed validation.
Never pass private images, crops, annotations, or credentials through the
adapter logs.
