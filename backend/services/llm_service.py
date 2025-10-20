from openai import OpenAI
import os
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Use xAI Grok API client
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            logger.warning("GROK_API_KEY environment variable not set. LLM features will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            logger.info("LLM service initialized with Grok API")
        self.model = "grok-4-fast-reasoning"
    
    def _format_chunks_for_context(self, chunks: List[str]) -> str:
        """Format RAG chunks into a well-structured context for the LLM"""
        if not chunks:
            return "No relevant context found in the documents."
        
        # Format chunks with clear separation and numbering
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            # Clean up the chunk text
            chunk_text = chunk.strip()
            if chunk_text:
                formatted_chunks.append(f"[Context Section {i}]\n{chunk_text}")
        
        if not formatted_chunks:
            return "No relevant context found in the documents."
        
        return "\n\n" + "\n\n---\n\n".join(formatted_chunks) + "\n\n"
    
    def generate_response(self, query: str, context: List[str], custom_prompt: Optional[str] = None) -> str:
        """Generate response using LLM with context from RAG"""
        
        # Format context from relevant chunks with better structure
        context_text = self._format_chunks_for_context(context)
        
        # Default prompt or custom prompt
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = """You are an AI assistant that analyzes documents and provides helpful summaries and explanations.

Your task is to:
1. Carefully read and understand the context provided from the documents
2. Answer the user's question accurately based on the context
3. Cite specific sections when making claims
4. If the context doesn't contain sufficient information, clearly state what is missing
5. Provide comprehensive, well-structured answers

When referencing information, mention which context section it came from (e.g., "According to Context Section 2...").
"""
        
        user_prompt = f"""Based on the following context from uploaded documents, please answer my question.

{context_text}

Question: {query}

Please provide a comprehensive answer based on the context above. If you reference specific information, mention which context section it came from.
"""
        
        try:
            if self.client is None:
                logger.error("LLM client is not configured")
                return "LLM service is not configured. Please set GROK_API_KEY environment variable."
            
            logger.info(f"Generating response for query: {query[:100]}...")
            logger.debug(f"Context chunks: {len(context)}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.info(f"Successfully generated response ({len(result)} chars)")
            return result
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return f"Error generating response: {str(e)}"
    
    def summarize_document(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of the document"""
        if not self.client:
            return "LLM service is not configured. Please set GROK_API_KEY environment variable."
        
        # Truncate very long texts to avoid token limits
        max_input_chars = 8000
        if len(text) > max_input_chars:
            text = text[:max_input_chars] + "... (text truncated)"
        
        prompt = f"""Please provide a concise summary of the following document.

Document:
{text}

Summary (aim for ~{max_length} characters):
"""
        
        try:
            logger.info(f"Generating summary for document ({len(text)} chars)")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, accurate summaries of documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length // 2,  # Rough token estimate
                temperature=0.5
            )
            
            result = response.choices[0].message.content
            logger.info(f"Successfully generated summary ({len(result)} chars)")
            return result
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return f"Error generating summary: {str(e)}"
    
    def analyze_image(self, image_path: str) -> str:
        """Analyze image content using Grok Vision (if available)"""
        try:
            # This would require Grok Vision API
            # For now, return a placeholder
            logger.warning("Image analysis requested but Grok Vision API is not configured")
            return "Image analysis feature requires Grok Vision API configuration."
        
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"