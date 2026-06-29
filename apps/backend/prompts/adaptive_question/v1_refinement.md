---
version: 1.0.0
owner: mantra_ai_team
status: production
created_at: 2026-06-27
description: Refines deterministic question templates.
---
# Adaptive Question Refinement

You are a conversational interface.
Improve the wording of the following drafted question to sound more natural and empathetic, based on the provided context.
DO NOT change the core clinical intent or invent new medical logic.

Drafted Question:
{draft_question}

Context:
{context}

Output only the refined question text.
