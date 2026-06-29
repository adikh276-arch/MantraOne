---
version: 1.0.0
owner: mantra_ai_team
status: production
created_at: 2026-06-27
description: Generates high-level health summaries.
---
# Health Summary

Generate a concise {summary_timeframe} summary for the following member/family based strictly on the provided structured context.
Do not summarize arbitrary conversation fragments, only validated clinical facts.

Context:
{health_context}

Output MUST be valid JSON adhering strictly to the provided Pydantic schema. Do not include markdown formatting or prose.
