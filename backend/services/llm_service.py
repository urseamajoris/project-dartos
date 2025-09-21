from openai import OpenAI
import os
from typing import List, Optional

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"
    
    def generate_response(self, query: str, context: List[str], custom_prompt: Optional[str] = None) -> str:
        """Generate response using LLM with context from RAG"""
        
        # Build context from relevant chunks
        context_text = "\n\n".join(context) if context else "No relevant context found."
        
        # Default prompt or custom prompt
        if custom_prompt:
            system_prompt = custom_prompt
        else:
            system_prompt = """You are an AI assistant that analyzes documents and provides helpful summaries and explanations.
            Use the provided context to answer the user's question accurately and comprehensively.
            If the context doesn't contain relevant information, state that clearly."""
        
        user_prompt = f"""
        Context from documents:
        {context_text}
        
        Question: {query}
        
        Please provide a comprehensive answer based on the context above.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def summarize_document(self, text: str) -> str:
        """Generate a summary of the document"""
        prompt = f"""
        Please provide a concise summary of the following document:
        
        {text}
        
        Summary:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def analyze_image(self, image_path: str) -> str:
        """Analyze image content using GPT-4 Vision (if available)"""
        try:
            # This would require GPT-4 Vision API
            # For now, return a placeholder
            return "Image analysis feature requires GPT-4 Vision API configuration."
        
        except Exception as e:
            return f"Error analyzing image: {str(e)}"