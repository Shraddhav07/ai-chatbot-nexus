"""
FastAPI Backend Application for Module 6 Chatbot.
Demonstrates:
  - Activity 2: Backend application with CORS support
  - Activity 3: Secure API key validation
  - Activity 4: Input validation
  - Activity 5 & 6: API error handling & timeout safety
  - Activity 7: Cleaned response delivery
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from config import get_api_credentials
from chatbot import validate_user_input, send_chat_message

app = FastAPI(
    title="Nexus AI Backend API",
    description="Adaptive multi-persona AI backend service with dynamic system prompts, input validation, and CORS support.",
    version="1.0.0"
)

# Activity 2: Supporting cross-origin requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development/testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


PERSONA_PROMPTS = {
    "teacher": (
        "You are an expert, patient, and encouraging Teacher Assistant. "
        "Your role is to help students learn effectively. Break down complex concepts into simple, "
        "digestible steps. Use clear analogies, concrete real-world examples, and check for understanding."
    ),
    "summarizer": (
        "You are a professional Executive Text Summarizer. "
        "Produce high-quality summaries with: 1. TL;DR (1-2 sentences), "
        "2. Key Takeaways (bulleted), 3. Actionable Points. Be concise and eliminate fluff."
    ),
    "coach": (
        "You are a veteran Senior Hiring Manager and Interview Coach. "
        "Conduct mock interviews, ask behavioral (STAR method) or technical questions, "
        "critique candidate answers, and suggest improved phrasing."
    ),
    "travel": (
        "You are an experienced, enthusiastic Global Travel Guide. "
        "Provide detailed travel recommendations, day-by-day itineraries, cultural etiquette, "
        "local food must-tries, hidden gems, and practical transit tips."
    ),
    "assistant": "You are a helpful, courteous, and knowledgeable AI assistant."
}


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to be processed by the chatbot")
    strip_markdown: Optional[bool] = Field(default=False, description="Optionally strip markdown formatting")
    persona: Optional[str] = Field(default="assistant", description="Selected AI persona (teacher, summarizer, coach, travel, assistant)")


class ChatResponse(BaseModel):
    success: bool
    reply: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    active_persona: Optional[str] = None


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Intellipaat Module 6 Chatbot Backend API",
        "docs_url": "/docs",
        "available_personas": list(PERSONA_PROMPTS.keys())
    }


@app.get("/health")
def health_check():
    """
    Validates backend health and checks whether API credentials are configured.
    """
    creds = get_api_credentials(require_key=False)
    has_key = creds is not None
    provider = creds.get("provider") if creds else None
    model = creds.get("model") if creds else None

    return {
        "status": "healthy" if has_key else "configuration_required",
        "api_key_configured": has_key,
        "active_provider": provider,
        "active_model": model,
        "available_personas": list(PERSONA_PROMPTS.keys())
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Receives user prompt, validates input, applies selected persona's dynamic
    system prompt, interacts with LLM, and returns sanitized response.
    """
    # Activity 4: Validate user input
    is_valid, processed_text, is_exit = validate_user_input(request.message)

    if is_exit:
        return ChatResponse(
            success=True,
            reply="Session termination requested. Goodbye!",
            active_persona=request.persona
        )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=processed_text
        )

    # Resolve dynamic system prompt from persona
    persona_key = (request.persona or "assistant").lower()
    system_prompt = PERSONA_PROMPTS.get(persona_key, PERSONA_PROMPTS["assistant"])

    # Activity 3 & 5 & 6 & 7: Process chat via backend engine
    result = send_chat_message(
        prompt=processed_text,
        strip_markdown=request.strip_markdown or False,
        system_prompt=system_prompt
    )

    if not result["success"]:
        return ChatResponse(
            success=False,
            error_type=result.get("error_type"),
            error_message=result.get("error_message"),
            active_persona=persona_key
        )

    return ChatResponse(
        success=True,
        reply=result.get("reply"),
        active_persona=persona_key
    )


if __name__ == "__main__":
    import uvicorn
    # Verify credentials at startup
    get_api_credentials(require_key=True)
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
