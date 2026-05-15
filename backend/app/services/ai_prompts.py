from __future__ import annotations

from textwrap import dedent


class AIPromptTemplates:
    @staticmethod
    def task_extraction_system_prompt() -> str:
        return dedent(
            """
            You are a precise AI assistant for a personal task manager.
            Your job is to extract structured task information from Vietnamese chat.
            Return JSON only. Do not include markdown fences or extra commentary.
            """
        ).strip()

    @staticmethod
    def task_extraction_user_prompt(message: str) -> str:
        return dedent(
            f"""
            Extract the user's intent and task details from this message.

            Return valid JSON with this exact shape:
            {{
              "reply": "short Vietnamese reply",
              "intent": "create_task|update_task|delete_task|list_tasks|plan_today|daily_summary|unknown",
              "needs_confirmation": true,
              "missing_fields": ["field_name"],
              "parsed_task": {{
                "title": "string or null",
                "description": "string or null",
                "category": "string or null",
                "priority": "low|medium|high|urgent|null",
                "due_at": "ISO datetime string or null",
                "reminder_at": "ISO datetime string or null"
              }}
            }}

            Rules:
            - Reply in Vietnamese.
            - If time/date is ambiguous, set needs_confirmation=true.
            - If no task can be extracted, set intent="unknown".
            - If the user asks for a list/plan/summary, keep parsed_task null.

            User message: {message}
            """
        ).strip()

    @staticmethod
    def daily_planner_prompt(task_summary: str) -> str:
        return dedent(
            f"""
            You are helping a user plan today.
            Based on the task summary below, produce a short Vietnamese answer
            with the 3 most important tasks and a concise recommendation.

            Task summary:
            {task_summary}
            """
        ).strip()

    @staticmethod
    def daily_summary_prompt(summary_payload: str) -> str:
        return dedent(
            f"""
            You are generating a brief Vietnamese daily summary for a personal task manager.
            Use the data below to summarize progress and suggest the next step.

            Data:
            {summary_payload}
            """
        ).strip()
