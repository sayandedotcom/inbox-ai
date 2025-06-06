from langchain.prompts import PromptTemplate
from config import OPENAI_API_KEY  # Import your API key from config
from langchain_openai import ChatOpenAI
from utils.logger import get_logger

from utils.formatter import clean_text, format_email

logger = get_logger(__name__)


def filter_email(email: dict) -> str:
    """
    Uses an LLM to analyze the email and classify its type.
    
    The email is classified as one of:
    - "spam"
    - "urgent"
    - "needs_review"
    - "informational"
    
    Arguments:
        email (dict): The email to be analyzed. Expected keys: "subject", "body".
    
    Returns:
        str: The classification result.
    """
    
    prompt_template = PromptTemplate(
        input_variables=["subject", "content"],
        template=(
            "Analyze the following email with subject: {subject} and content: {content} "
            "and classify the email type. "
            "Classify it as 'spam', 'urgent', 'informational', or 'needs review'."
        )
    )
    
    prompt = prompt_template.format(
        subject=email.get("subject", ""),
        content=email.get("body", "")
    )
    
    model = ChatOpenAI(
        model="openai/gpt-4.1",
        temperature=0.5,
        openai_api_key=OPENAI_API_KEY
    )
    
    classification_result = model.invoke(prompt) 
    
    classification_text = clean_text(str(classification_result))    
    
    # logss the raw model output for debugging.
    logger.debug("Raw model output: %s", classification_text)
    
    # Check for 'needs review' first
    if "'needs review'" in classification_text or "needs review" in classification_text:
        return "needs_review"
    elif "urgent" in classification_text:
        return "urgent"
    elif "spam" in classification_text:
        return "spam"
    else:
        return "informational"