"""
AI Study Assistant Agent - Core Agent Controller & Task Handlers
================================================================
Subject: AI Agent Development
Module: agent.py

Architecture Overview:
----------------------
This file implements an AI Agent Controller that applies the "Router / Orchestrator"
pattern. The agent receives an academic task from the frontend (app.py), validates
the input and credentials, selects the appropriate prompt template, and dispatches
the task to the configured Large Language Model (Google Gemini or OpenAI).

Core Functions:
1. ask_question()   -> Explains complex concepts with step-by-step clarity & analogies.
2. summarize_notes() -> Condenses study notes into summaries, bullet points & keywords.
3. generate_quiz()   -> Creates practice questions (MCQs or conceptual review).
4. route_task()      -> Central controller that routes requests to the right handler.
"""

import os
import hashlib
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# =====================================================================
# SYSTEM PERSONA, SUPPORTED MODELS & PROMPT TEMPLATES
# =====================================================================

PREFERRED_GEMINI_MODEL = "gemini-3.5-flash-lite"
DOCUMENTED_FLASH_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.8-pro"]
DEFAULT_REQUEST_TIMEOUT = 45.0

# Caches for verified model and model list, tracked by API key hash to refresh on key change
_MODEL_SELECTION_CACHE: Dict[str, str] = {}
_AVAILABLE_MODELS_CACHE: Dict[str, list] = {}
_LAST_KEY_HASH: Optional[str] = None


def _get_key_hash_and_refresh_cache(api_key: str) -> str:
    """
    Computes a secure hash of the API key and refreshes (invalidates) the model cache
    whenever the API key changes.
    """
    global _LAST_KEY_HASH, _MODEL_SELECTION_CACHE, _AVAILABLE_MODELS_CACHE
    k_hash = hashlib.sha256(api_key.strip().encode("utf-8")).hexdigest()
    if _LAST_KEY_HASH != k_hash:
        _MODEL_SELECTION_CACHE.clear()
        _AVAILABLE_MODELS_CACHE.clear()
        _LAST_KEY_HASH = k_hash
    return k_hash


def resolve_active_gemini_model(api_key: Optional[str] = None) -> str:
    """
    Verifies the exact model ID for 'gemini-3.5-flash-lite' against the models returned
    by the configured Gemini API key.
    
    1. If supported, returns the verified model ID directly. Neither gemini-2.5-flash
       nor gemini-3.8-flash will be selected when the preferred model is available.
    2. If unavailable, raises a clear RuntimeError displaying the actual supported Flash
       model IDs returned by the API key, without silently switching to an unverified model.
    3. Caches model selection per API key hash to avoid repeated discovery, refreshing
       automatically when the API key changes.
    """
    resolved_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_key:
        return PREFERRED_GEMINI_MODEL

    key_hash = _get_key_hash_and_refresh_cache(resolved_key)
    if key_hash in _MODEL_SELECTION_CACHE:
        return _MODEL_SELECTION_CACHE[key_hash]

    try:
        import google.generativeai as genai
        genai.configure(api_key=resolved_key)

        available = []
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                clean_name = m.name.replace("models/", "")
                # Exclude deprecated legacy models if present
                if not any(clean_name.startswith(p) for p in ("gemini-1.", "gemini-1.0", "gemini-pro")):
                    available.append(clean_name)

        if available:
            _AVAILABLE_MODELS_CACHE[key_hash] = available

            # 1. Verify exact model ID for gemini-3.5-flash-lite
            exact_match = None
            if PREFERRED_GEMINI_MODEL in available:
                exact_match = PREFERRED_GEMINI_MODEL
            else:
                variants = [m for m in available if m.startswith(PREFERRED_GEMINI_MODEL)]
                if variants:
                    exact_match = variants[0]

            if exact_match:
                _MODEL_SELECTION_CACHE[key_hash] = exact_match
                return exact_match

            # 2. If unavailable: do not silently switch to an unverified model
            flash_models = [m for m in available if "flash" in m.lower()]
            flash_list_str = ", ".join(f"'{m}'" for m in flash_models) if flash_models else "None"

            raise RuntimeError(
                f"The preferred model '{PREFERRED_GEMINI_MODEL}' is unavailable for your Gemini API key. "
                f"Actual supported Flash models returned by your API key: [{flash_list_str}]. "
                f"Please choose one of these supported models in Settings or verify your account access."
            )

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to query Gemini API models: {str(e)}")

    return PREFERRED_GEMINI_MODEL


def get_supported_gemini_models(api_key: Optional[str] = None) -> list:
    """
    Retrieves available Gemini models supporting 'generateContent' from the API.
    Places the verified preferred model first if available.
    Refreshes cache when API key changes.
    """
    resolved_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_key:
        return DOCUMENTED_FLASH_MODELS

    key_hash = _get_key_hash_and_refresh_cache(resolved_key)

    if key_hash in _AVAILABLE_MODELS_CACHE:
        cached = _AVAILABLE_MODELS_CACHE[key_hash]
        active = _MODEL_SELECTION_CACHE.get(key_hash)
        if active and active in cached:
            return [active] + [m for m in cached if m != active]
        return cached

    try:
        import google.generativeai as genai
        genai.configure(api_key=resolved_key)

        available = []
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                clean_name = m.name.replace("models/", "")
                if not any(clean_name.startswith(p) for p in ("gemini-1.", "gemini-1.0", "gemini-pro")):
                    available.append(clean_name)

        if available:
            _AVAILABLE_MODELS_CACHE[key_hash] = available

            # Check if preferred model is supported
            if PREFERRED_GEMINI_MODEL in available:
                _MODEL_SELECTION_CACHE[key_hash] = PREFERRED_GEMINI_MODEL
                return [PREFERRED_GEMINI_MODEL] + [m for m in available if m != PREFERRED_GEMINI_MODEL]

            variants = [m for m in available if m.startswith(PREFERRED_GEMINI_MODEL)]
            if variants:
                chosen = variants[0]
                _MODEL_SELECTION_CACHE[key_hash] = chosen
                return [chosen] + [m for m in available if m != chosen]

            # If preferred model is not available, return available models prioritizing other Flash models
            flash_models = [m for m in available if "flash" in m.lower()]
            other_models = [m for m in available if m not in flash_models]
            return flash_models + other_models

    except Exception:
        pass

    return DOCUMENTED_FLASH_MODELS


SYSTEM_TUTOR_PERSONA = (
    "You are an encouraging, expert AI Academic Tutor. "
    "Provide clear, structured, and high-yield study explanations without filler or unnecessary preambles. "
    "Use clean Markdown headers, bullet points, and short intuitive analogies to maximize student retention."
)


# =====================================================================
# LLM INVOCATION WRAPPER (Gemini & OpenAI Support with Timeouts)
# =====================================================================

def call_llm(
    prompt: str,
    system_instruction: str = SYSTEM_TUTOR_PERSONA,
    provider: str = "Google Gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT
) -> str:
    """
    Unified caller for LLM providers with configurable timeout (default 45s) and quota protection.
    Does not repeatedly retry failed requests.
    """
    provider_clean = provider.strip().lower()

    # 1. Google Gemini Provider
    if "gemini" in provider_clean:
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Gemini API key is missing. Please configure it in Settings or set GEMINI_API_KEY in your .env file."
            )
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "The 'google-generativeai' package is not installed. Run: pip install google-generativeai"
            )

        genai.configure(api_key=resolved_key)
        
        # Determine verified model
        # If model is explicitly PREFERRED_GEMINI_MODEL or omitted: verify against actual API models
        if not model or model == PREFERRED_GEMINI_MODEL:
            target_model = resolve_active_gemini_model(resolved_key)
        else:
            # Check user-specified model against verified models for this key
            available_models = get_supported_gemini_models(resolved_key)
            if model not in available_models:
                flash_models = [m for m in available_models if "flash" in m.lower()]
                flash_list_str = ", ".join(f"'{m}'" for m in flash_models) if flash_models else "None"
                raise RuntimeError(
                    f"Selected model '{model}' is not supported by your Gemini API key. "
                    f"Actual supported Flash models returned by your API key: [{flash_list_str}]."
                )
            target_model = model

        try:
            # Configure model with system instructions
            gemini_model = genai.GenerativeModel(
                model_name=target_model,
                system_instruction=system_instruction
            )
            # Pass timeout in request options to avoid infinite hangs (45s configurable default)
            response = gemini_model.generate_content(
                prompt,
                request_options={"timeout": timeout}
            )
        except Exception as e:
            err_msg = str(e)
            err_lower = err_msg.lower()
            if "404" in err_msg or "not found" in err_lower:
                available_models = get_supported_gemini_models(resolved_key)
                flash_models = [m for m in available_models if "flash" in m.lower()]
                flash_list_str = ", ".join(f"'{m}'" for m in flash_models) if flash_models else "None"
                raise RuntimeError(
                    f"Gemini model '{target_model}' was not found for your API key. "
                    f"Supported Flash models: [{flash_list_str}]. (Details: {err_msg})"
                )
            if "timeout" in err_lower or "deadline" in err_lower:
                raise RuntimeError(
                    f"Request timed out after {int(timeout)}s. Please check your connection or retry."
                )
            if "429" in err_msg or "quota" in err_lower or "resource_exhausted" in err_lower:
                raise RuntimeError(
                    "API rate limit or quota exceeded. Please wait a moment before trying again."
                )
            raise RuntimeError(f"Gemini API Error: {err_msg}")

        if not response.text:
            raise RuntimeError("The model returned an empty response. Please try rephrasing.")
        return response.text.strip()

    # 2. OpenAI Provider
    elif "openai" in provider_clean:
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OpenAI API key is missing. Please configure it in Settings or set OPENAI_API_KEY in your .env file."
            )
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "The 'openai' package is not installed. Run: pip install openai"
            )

        try:
            client = OpenAI(api_key=resolved_key, timeout=timeout)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=850
            )
            content = response.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            err_lower = err_msg.lower()
            if "timeout" in err_lower:
                raise RuntimeError(
                    f"Request timed out after {int(timeout)}s. Please check your internet connection or try again."
                )
            if "429" in err_msg or "quota" in err_lower or "rate_limit" in err_lower:
                raise RuntimeError(
                    "OpenAI rate limit or quota exceeded. Please check your plan limits."
                )
            raise RuntimeError(f"OpenAI API Error: {err_msg}")

        if not content:
            raise RuntimeError("The model returned an empty response. Please try rephrasing.")
        return content.strip()

    else:
        raise ValueError(f"Unsupported LLM provider: '{provider}'. Choose 'Google Gemini' or 'OpenAI'.")


# =====================================================================
# SPECIALIZED AGENT TASKS (Optimized for Speed & Conciseness)
# =====================================================================

def ask_question(
    question: str,
    subject: str = "",
    provider: str = "Google Gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT
) -> str:
    """
    Task Handler 1: Answer study-related questions.
    Provides concise, high-yield conceptual explanations with memorable analogies.
    """
    subject_prefix = f"Subject / Context: {subject}\n\n" if subject else ""
    prompt = f"""
{subject_prefix}Student Question:
\"\"\"{question}\"\"\"

Provide a high-yield, structured explanation in Markdown:
1. 💡 **Core Concept**: 1-2 sentence direct definition.
2. 📖 **Step-by-Step Breakdown**: Concise, clear explanation (bullet points).
3. 🌟 **Real-World Analogy**: One memorable, practical analogy.
4. 📌 **Key Takeaway**: One exam-prep memory hook.
Target conciseness: under 220 words.
"""
    return call_llm(
        prompt=prompt,
        system_instruction=SYSTEM_TUTOR_PERSONA,
        provider=provider,
        model=model,
        api_key=api_key,
        timeout=timeout
    )


def summarize_notes(
    notes: str,
    summary_mode: str = "Standard",
    provider: str = "Google Gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT
) -> str:
    """
    Task Handler 2: Summarize student lecture notes or textbook passages.
    Extracts high-yield executive summaries, bullet points, and key terms.
    """
    mode_instructions = {
        "Standard": "Provide a 2-sentence executive summary, followed by key bullet points, and core definitions.",
        "Quick Bullets": "Provide only punchy, high-yield bullet points for rapid revision.",
        "Key Definitions & Terms": "Extract all crucial terms, definitions, and formulas into a concise glossary."
    }.get(summary_mode, "Provide a balanced, high-yield summary.")

    prompt = f"""
Study Notes:
\"\"\"{notes}\"\"\"

Task: {mode_instructions}

Format using crisp Markdown:
- 📌 **Executive Overview**
- 🔑 **Key Takeaways**
- 🧠 **Definitions & Formulas**
Keep the output direct, structured, and free of filler text.
"""
    return call_llm(
        prompt=prompt,
        system_instruction=SYSTEM_TUTOR_PERSONA,
        provider=provider,
        model=model,
        api_key=api_key,
        timeout=timeout
    )


def generate_quiz(
    topic_or_notes: str,
    num_questions: int = 3,
    quiz_type: str = "Multiple Choice",
    provider: str = "Google Gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT
) -> str:
    """
    Task Handler 3: Generate practice questions from a topic or study material.
    Supports Multiple Choice Questions or Short Answer Review.
    """
    if quiz_type == "Multiple Choice":
        format_guide = """
Format each question as:
### Question [N]: [Question text]
- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

> **Correct Answer:** [Option Letter & short answer]
> **Explanation:** [1-sentence concise reason why this is correct]
"""
    else:
        format_guide = """
Format each question as:
### Question [N]: [Conceptual question]
> **Model Answer:** [Concise, direct answer]
> **Key Exam Points:** [1-2 critical keywords or points]
"""

    prompt = f"""
Topic / Material:
\"\"\"{topic_or_notes}\"\"\"

Generate exactly {num_questions} high-yield {quiz_type} questions for exam preparation.
Difficulty: Mixed (conceptual and application).

{format_guide}
Keep question texts concise and explanations direct.
"""
    return call_llm(
        prompt=prompt,
        system_instruction=SYSTEM_TUTOR_PERSONA,
        provider=provider,
        model=model,
        api_key=api_key,
        timeout=timeout
    )


# =====================================================================
# AGENT CONTROLLER / ROUTER
# =====================================================================

def route_task(
    task_type: str,
    payload: Dict[str, Any],
    provider: str = "Google Gemini",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = DEFAULT_REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """
    Central Agent Controller.
    Receives request parameters, validates them, and routes execution to the
    appropriate task handler. Catches runtime errors and returns a standardized response.
    
    Args:
        task_type: 'ask', 'summarize', or 'quiz'.
        payload: Dictionary containing inputs specific to the task.
        provider: 'Google Gemini' or 'OpenAI'.
        model: Model name.
        api_key: Optional explicit API key.
        timeout: Request timeout in seconds (default 45.0s).
        
    Returns:
        Dict: {"status": "success" | "error", "data": str, "message": str}
    """
    try:
        # Resolve active Gemini model if not specified or if set to preferred
        if "gemini" in provider.strip().lower() and (not model or model == PREFERRED_GEMINI_MODEL):
            model = resolve_active_gemini_model(api_key)

        # 1. Route: Ask a Question
        if task_type == "ask":
            question = payload.get("question", "").strip()
            subject = payload.get("subject", "").strip()

            if not question:
                return {
                    "status": "error",
                    "data": "",
                    "message": "Question cannot be empty. Please enter what you would like to learn."
                }

            result = ask_question(
                question=question,
                subject=subject,
                provider=provider,
                model=model,
                api_key=api_key,
                timeout=timeout
            )
            return {"status": "success", "data": result, "message": "Question answered successfully."}

        # 2. Route: Summarize Notes
        elif task_type == "summarize":
            notes = payload.get("notes", "").strip()
            mode = payload.get("mode", "Standard")

            if not notes:
                return {
                    "status": "error",
                    "data": "",
                    "message": "Notes cannot be empty. Please paste your lecture notes or text to summarize."
                }

            result = summarize_notes(
                notes=notes,
                summary_mode=mode,
                provider=provider,
                model=model,
                api_key=api_key,
                timeout=timeout
            )
            return {"status": "success", "data": result, "message": "Notes summarized successfully."}

        # 3. Route: Generate Quiz
        elif task_type == "quiz":
            topic = payload.get("topic_or_notes", "").strip()
            num_q = int(payload.get("num_questions", 3))
            q_type = payload.get("quiz_type", "Multiple Choice")

            if not topic:
                return {
                    "status": "error",
                    "data": "",
                    "message": "Please provide a topic or paste notes to generate quiz questions."
                }

            result = generate_quiz(
                topic_or_notes=topic,
                num_questions=num_q,
                quiz_type=q_type,
                provider=provider,
                model=model,
                api_key=api_key,
                timeout=timeout
            )
            return {"status": "success", "data": result, "message": "Quiz generated successfully."}

        # 4. Unknown Task
        else:
            return {
                "status": "error",
                "data": "",
                "message": f"Unknown agent task type: '{task_type}'. Valid options are 'ask', 'summarize', 'quiz'."
            }

    except Exception as e:
        # Return cleanly formatted error message to the UI
        return {
            "status": "error",
            "data": "",
            "message": f"Agent Execution Error: {str(e)}"
        }
