"""
Response Generator - Generates responses using LLM
"""
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """Generator for creating responses"""
    
    def __init__(self):
        """Initialize generator"""
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.use_llm = bool(self.api_key)
        
        if not self.use_llm:
            logger.warning("No API key found. Using simple responses.")
    
    def generate(self, query: str, context: str = None, conversation_history: list = None):
        """
        Generate response
        
        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous messages
            
        Returns:
            Generated response
        """
        try:
            if self.use_llm:
                return self._generate_with_llm(query, context, conversation_history)
            else:
                return self._generate_simple(query, context)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error. Please try again."
    
    def _generate_with_llm(self, query: str, context: str = None, conversation_history: list = None):
        """Generate using LLM API"""
        try:
            prompt = self._build_prompt(query, context, conversation_history)
            
            # Try OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                return self._generate_with_openai(prompt)
            
            # Try Anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                return self._generate_with_anthropic(prompt)
            
            return self._generate_simple(query, context)
            
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return self._generate_simple(query, context)
    
    def _generate_with_openai(self, prompt: str):
        """Generate using OpenAI v1.0+"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,  # Increased for professional responses
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            raise
    
    def _generate_with_anthropic(self, prompt: str):
        """Generate using Anthropic"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic error: {str(e)}")
            raise
    
    def _generate_simple(self, query: str, context: str = None):
        """Simple fallback responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! How can I help you today?"
        
        elif any(word in query_lower for word in ['how are you']):
            return "I'm doing well, thank you! How can I assist you?"
        
        elif 'thank' in query_lower:
            return "You're welcome! Is there anything else I can help you with?"
        
        elif any(word in query_lower for word in ['bye', 'goodbye']):
            return "Goodbye! Feel free to come back if you need help."
        
        elif context:
            return f"Based on the information: {context}\n\nIs there anything specific you'd like to know?"
        
        else:
            return "I understand. Could you provide more details so I can assist you better?"
    
    def _build_prompt(self, query: str, context: str = None, conversation_history: list = None):
        """Build prompt for LLM - Professional chatbot quality"""
        prompt_parts = []
        
        # System role
        prompt_parts.append(
            "You are an expert e-commerce sales assistant with deep product knowledge. "
            "Your goal is to help customers find exactly what they need while providing "
            "an exceptional shopping experience. Communicate like a friendly, knowledgeable "
            "retail professional - not a robot."
        )
        
        # Available products context
        if context:
            prompt_parts.append(f"\n=== AVAILABLE PRODUCTS ===\n{context}\n")
        
        # Conversation history for context
        if conversation_history:
            prompt_parts.append("=== CONVERSATION HISTORY ===")
            for msg in conversation_history[-5:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role.capitalize()}: {content}")
            prompt_parts.append("")
        
        # Current customer query
        prompt_parts.append(f"=== CUSTOMER INQUIRY ===\nCustomer: {query}\n")
        
        # Professional response guidelines
        prompt_parts.append(
            "=== RESPONSE GUIDELINES ===\n"
            "1. DIRECT ANSWERS: If asked 'do you have X?', start with YES or NO\n"
            "2. PRODUCT DETAILS: Provide specific info (sizes, colors, prices, materials)\n"
            "3. RELEVANCE: Only mention products that directly answer the question\n"
            "4. CONVERSATIONAL: Use natural language, contractions, friendly tone\n"
            "5. ALTERNATIVES: If exact match unavailable, suggest 2-3 similar options\n"
            "6. ENGAGEMENT: End with a helpful question or next step\n"
            "7. CONCISENESS: Keep under 150 words unless detailed explanation needed\n"
            "8. PROFESSIONALISM: Avoid phrases like 'Based on the information' or 'Is there anything specific'\n"
            "9. VALUE-ADDING: Highlight unique features, benefits, or styling tips\n"
            "10. PERSONALIZATION: Reference their specific needs from the query\n\n"
            
            "TONE EXAMPLES:\n"
            "❌ BAD: 'Based on the information: [Source 1]... Is there anything specific you'd like to know?'\n"
            "✅ GOOD: 'Yes! We have Lawn Suits available in your preferred style. Let me share the details...'\n\n"
            
            "❌ BAD: 'The product catalog shows...'\n"
            "✅ GOOD: 'Perfect choice! Our Lawn Suits are bestsellers because...'\n\n"
            
            "RESPONSE FORMAT:\n"
            "- Start with direct answer or acknowledgment\n"
            "- Provide 3-5 key details in natural flow\n"
            "- End with engaging question or call-to-action\n"
            "- Use bullet points ONLY if listing 4+ items\n"
            "- Otherwise use conversational paragraphs\n\n"
            
            "NOW RESPOND TO THE CUSTOMER:"
        )
        
        return "\n".join(prompt_parts)