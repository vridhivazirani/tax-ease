"""GigSaathi — Gemini Agent Service.

The core agentic AI layer. Uses Gemini's function calling to automatically
decide which tools to invoke based on user questions, execute them in sequence,
and generate natural language responses grounded in real data.

Supports streaming responses via Server-Sent Events (SSE).
"""

import json
from datetime import datetime

from google import genai
from google.genai import types

from app.config import settings
from app.agent.tools import (
    get_income_summary,
    calculate_tax,
    find_deductions,
    generate_itr_summary,
    check_deadlines,
)


# ── System Prompt ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are GigSaathi (गिग साथी), an AI-powered tax and compliance assistant built specifically for India's gig economy workers — Swiggy delivery partners, Uber drivers, Upwork freelancers, Fiverr gig workers, and anyone earning from multiple platforms.

## YOUR PERSONALITY
- Friendly, supportive, and patient — like a knowledgeable friend who happens to understand Indian tax law
- You explain complex tax concepts in simple, everyday Hindi-English (Hinglish) when appropriate
- You celebrate small wins ("Great news! You're getting a refund!")
- You never make the user feel stupid for not knowing tax rules

## CRITICAL RULES
1. **ALWAYS use your tools to fetch real data.** NEVER make up numbers, estimates, or assumptions.
2. When asked about income → call get_income_summary() FIRST
3. When asked about tax → call calculate_tax() to get EXACT figures
4. When asked about deductions → call find_deductions()
5. When asked about ITR/filing → call generate_itr_summary()
6. When asked about deadlines → call check_deadlines()
7. You CAN chain multiple tools if needed (e.g., first get income, then calculate tax)
8. All amounts must be in Indian Rupees (₹) with proper comma formatting (₹1,23,456)
9. Always mention the financial year (FY 2025-26) for context
10. After showing tax calculations, PROACTIVELY mention upcoming deadlines

## FORMATTING
- Use ₹ symbol for all amounts
- Format large numbers Indian style: ₹1,23,456 (not ₹123,456)
- Use bullet points for breakdowns
- Bold important numbers
- Use emojis sparingly but effectively (📊 💰 ⚠️ ✅ 📅)

## WHAT YOU CANNOT DO
- File the actual ITR (you prepare the data; the user files it)
- Access the Income Tax Department portal
- Provide legal advice — you provide tax information and calculations
- Guarantee that your calculations will match the IT department's exactly

## CONTEXT
- Financial Year: FY 2025-26 (April 2025 to March 2026)
- Assessment Year: AY 2026-27
- Default tax regime: New Tax Regime under Section 115BAC
- You understand Section 44ADA (Presumptive Taxation for professionals)
- You know all 4 advance tax deadlines: June 15, September 15, December 15, March 15
"""

# ── Tool Definitions ────────────────────────────────────────────────

# Map of tool names to their async implementations
TOOL_FUNCTIONS = {
    "get_income_summary": get_income_summary,
    "calculate_tax": calculate_tax,
    "find_deductions": find_deductions,
    "generate_itr_summary": generate_itr_summary,
    "check_deadlines": check_deadlines,
}

# Tool declarations for Gemini function calling — explicit schemas
# (async functions can't be passed directly to the SDK)
TOOL_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_income_summary",
            description=(
                "Fetches the user's complete income breakdown by platform and month. "
                "Use when the user asks about their earnings, income, how much they made, "
                "or anything related to their payment history."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {"type": "STRING", "description": "The unique identifier of the user."},
                    "financial_year": {"type": "STRING", "description": "The financial year to query. Defaults to 2025-26."},
                },
                "required": ["user_id"],
            },
        ),
        types.FunctionDeclaration(
            name="calculate_tax",
            description=(
                "Calculates the user's total tax liability for the current financial year. "
                "Use when the user asks how much tax they owe, their tax liability, "
                "whether they need to pay tax, or anything about tax computation."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {"type": "STRING", "description": "The unique identifier of the user."},
                },
                "required": ["user_id"],
            },
        ),
        types.FunctionDeclaration(
            name="find_deductions",
            description=(
                "Identifies claimable deductions based on the user's occupation and income. "
                "Use when the user asks about deductions, expenses they can claim, "
                "ways to reduce tax, or tax-saving options."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {"type": "STRING", "description": "The unique identifier of the user."},
                },
                "required": ["user_id"],
            },
        ),
        types.FunctionDeclaration(
            name="generate_itr_summary",
            description=(
                "Generates a structured ITR-4 (Sugam) field mapping ready for filing. "
                "Use when the user asks about filing ITR, wants their ITR summary, "
                "or asks for a tax return document."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {"type": "STRING", "description": "The unique identifier of the user."},
                },
                "required": ["user_id"],
            },
        ),
        types.FunctionDeclaration(
            name="check_deadlines",
            description=(
                "Checks upcoming advance tax deadlines and amounts due. "
                "Use when the user asks about deadlines, when to pay tax, "
                "advance tax dates, or if they have any upcoming tax obligations."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "user_id": {"type": "STRING", "description": "The unique identifier of the user."},
                },
                "required": ["user_id"],
            },
        ),
    ]
)


class GigSaathiAgent:
    """Gemini-powered agent with function calling for tax assistance."""

    def __init__(self):
        """Initialize the agent. Gemini client is lazy-loaded on first chat."""
        self._client = None
        self.model = settings.GEMINI_MODEL
        # Per-user conversation histories
        self._conversations: dict[str, list] = {}

    @property
    def client(self):
        """Lazy-initialize the Gemini client on first access."""
        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def _get_history(self, user_id: str) -> list:
        """Get or create conversation history for a user."""
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        return self._conversations[user_id]

    def clear_history(self, user_id: str):
        """Clear conversation history for a user."""
        self._conversations.pop(user_id, None)

    async def chat(self, user_id: str, message: str) -> dict:
        """Process a user message through the agent with tool calling.

        This implements the full function-calling loop:
        1. Send user message + tool declarations to Gemini
        2. If Gemini returns a function call → execute it
        3. Send the function result back to Gemini
        4. Repeat until Gemini returns a text response
        5. Return the final text response

        Args:
            user_id: The user's unique identifier (injected into tool calls).
            message: The user's natural language message.

        Returns:
            Dictionary with:
                - response: The agent's text response
                - tools_called: List of tools that were invoked
                - tool_results: Raw results from each tool call
        """
        history = self._get_history(user_id)
        tools_called = []
        tool_results = []

        # Add user message to history
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )
        history.append(user_content)

        # Function calling loop
        max_iterations = 10  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            response = self.client.models.generate_content(
                model=self.model,
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[TOOL_DECLARATIONS],
                    temperature=0.7,
                    max_output_tokens=4096,
                ),
            )

            # Check if the response contains function calls
            candidate = response.candidates[0]
            parts = candidate.content.parts

            has_function_call = any(
                part.function_call is not None for part in parts
            )

            if not has_function_call:
                # No more tool calls — we have the final text response
                history.append(candidate.content)
                final_text = response.text or "I'm sorry, I couldn't generate a response."
                break
            else:
                # Process function calls
                history.append(candidate.content)
                function_response_parts = []

                for part in parts:
                    if part.function_call is None:
                        continue

                    fn_call = part.function_call
                    fn_name = fn_call.name
                    fn_args = dict(fn_call.args) if fn_call.args else {}

                    # Inject user_id into all tool calls
                    if "user_id" in fn_args or fn_name in TOOL_FUNCTIONS:
                        fn_args["user_id"] = user_id

                    tools_called.append(fn_name)

                    # Execute the tool
                    try:
                        fn = TOOL_FUNCTIONS.get(fn_name)
                        if fn is None:
                            result = {"error": f"Unknown tool: {fn_name}"}
                        else:
                            result = await fn(**fn_args)

                        tool_results.append({"tool": fn_name, "result": result})
                    except Exception as e:
                        result = {"error": f"Tool execution failed: {str(e)}"}
                        tool_results.append({"tool": fn_name, "error": str(e)})

                    # Build function response part
                    function_response_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fn_name,
                                response=result,
                            )
                        )
                    )

                # Add function responses to history
                fn_response_content = types.Content(
                    role="user",
                    parts=function_response_parts,
                )
                history.append(fn_response_content)
        else:
            final_text = "I ran into a loop processing your request. Please try again."

        return {
            "response": final_text,
            "tools_called": tools_called,
            "tool_results": tool_results,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
agent = GigSaathiAgent()
