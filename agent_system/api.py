"""FastAPI application for the agent system."""
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.agent import create_agent
from src.utils.logger import setup_logger
from config import get_settings

# Initialize settings and logger
settings = get_settings()

# Setup root logger so all modules can output logs
import logging
root_logger = setup_logger(
    "",  # Empty string = root logger
    log_level=settings.log_level,
    log_file=settings.log_file
)

# Also setup named logger for this module
logger = logging.getLogger("agent_api")
logger.setLevel(settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="Intelligent Agent API",
    description="Production-grade intelligent agent for task processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for query processing."""
    
    user_query: str = Field(
        ...,
        description="The user's question or request",
        min_length=1,
        max_length=10000
    )
    mode_type: Optional[str] = Field(
        None,
        description="Optional task type override (simple_interaction, comparison_evaluation, etc.)"
    )
    enable_web_search: Optional[bool] = Field(
        None,
        description="Optional override for web search enablement"
    )
    deep_thinking: bool = Field(
        False,
        description="Enable deep thinking mode: multi-step recall with QA pairs (slower but more comprehensive)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for multi-turn conversation (auto-loads history if exists)"
    )
    
    # Direct content mode (for small documents)
    content: Optional[str] = Field(
        None,
        description="Full document content. If provided and small enough, will be used directly instead of recall"
    )
    force_recall: bool = Field(
        False,
        description="If True, always use recall even when content is provided and small"
    )
    
    # Recall configuration (overrides environment variables)
    recall_index_names: Optional[list] = Field(
        None,
        description="List of index names to search in recall API. If not provided, uses default from environment"
    )
    recall_doc_ids: Optional[list] = Field(
        None,
        description="List of document IDs to filter in recall API. If not provided, uses default from environment"
    )


class QueryResponse(BaseModel):
    """Response model for query processing."""
    
    success: bool = Field(..., description="Whether the query was processed successfully")
    session_id: str = Field(..., description="Session ID for this query")
    detected_intent: Optional[str] = Field(None, description="Detected task intent")
    plan: Optional[dict] = Field(None, description="Execution plan (if applicable)")
    final_answer: str = Field(..., description="Final answer to the user's query")
    execution_time: float = Field(..., description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if any")
    
    # Session context statistics
    session_total_tokens: Optional[int] = Field(None, description="Total tokens used in this session")
    session_message_count: Optional[int] = Field(None, description="Total messages in this session")
    compression_threshold: Optional[int] = Field(None, description="Token threshold for triggering compression")
    tokens_until_compression: Optional[int] = Field(None, description="Remaining tokens before compression is triggered")


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    logger.info("Initializing agent...")
    
    try:
        # Agent is configured via environment variables
        agent = create_agent()
        logger.info("Agent initialized successfully")
        logger.info(f"Recall API: {settings.recall_api_url}")
        logger.info(f"Web search enabled: {settings.enable_web_search}")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down agent API...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Intelligent Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "status": "healthy",
        "agent_ready": True
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query through the intelligent agent.
    
    Supports multi-turn conversation: provide session_id to continue a conversation,
    or omit it to start a new one.
    
    Args:
        request: Query request containing user query and optional parameters
        
    Returns:
        QueryResponse with the answer and metadata
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    logger.info(f"Received query [session: {request.session_id or 'new'}]: {request.user_query[:100]}...")
    
    try:
        result = agent.process_query(
            user_query=request.user_query,
            mode_type=request.mode_type,
            enable_web_search=request.enable_web_search,
            deep_thinking=request.deep_thinking,
            session_id=request.session_id,
            content=request.content,
            force_recall=request.force_recall,
            recall_index_names=request.recall_index_names,
            recall_doc_ids=request.recall_doc_ids
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get the conversation history for a session.
    
    Args:
        session_id: Session ID to retrieve history for
        
    Returns:
        List of messages in the conversation
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        history = agent.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/async")
async def process_query_async(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process a query asynchronously in the background.
    
    Args:
        request: Query request
        background_tasks: FastAPI background tasks
        
    Returns:
        Immediate response with session ID
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    import uuid
    session_id = request.session_id or str(uuid.uuid4())
    
    # Add task to background
    background_tasks.add_task(
        agent.process_query,
        request.user_query,
        request.mode_type,
        request.enable_web_search,
        request.deep_thinking,
        session_id
    )
    
    return {
        "session_id": session_id,
        "status": "processing",
        "message": "Query is being processed in the background"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level=settings.log_level.lower()
    )

