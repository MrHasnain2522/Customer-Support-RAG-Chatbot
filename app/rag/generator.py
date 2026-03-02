"""
Response Generator - Generates responses using LLM
Fixed:
  1. OpenAI Client initialization (removed potential proxy conflicts)
  2. Updated Anthropic model to claude-3-5-sonnet-20241022
  3. Added High-Performance 10/10 Accuracy Prompting (Advanced)
  4. Restored comprehensive debug logging
  5. Increased max_tokens to allow full lists and policy details
"""
import os
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ResponseGenerator:
    """Generator for creating responses with full transparency logging"""
    
    def __init__(self):
        """Initialize generator and check API keys"""
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.use_llm = bool(self.api_key)
        
        print("\n===== GENERATOR INIT DEBUG =====")
        print(f"API KEY FOUND: {self.use_llm}")
        print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
        print(f"ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not Set'}")
        print(f"MODEL CONFIGURED: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
        print("================================\n")

        if not self.use_llm:
            logger.warning("No API key found. Using simple fallback responses.")
        else:
            logger.info(f"ResponseGenerator initialized. LLM enabled: {self.use_llm}")
    
    def generate(self, query: str, context: str = None, conversation_history: list = None):
        """Generate response with comprehensive debug tracking"""
        try:
            print(f"\n========== GENERATE DEBUG ==========")
            print(f"QUERY: {query}")
            if context:
                print(f"CONTEXT LENGTH: {len(context)} characters")
                print(f"CONTEXT PREVIEW: {context[:200]}...")
            else:
                print("CONTEXT: [EMPTY] - Warning: Information will be generic.")
            print(f"USE LLM: {self.use_llm}")
            print(f"====================================\n")

            if self.use_llm:
                return self._generate_with_llm(query, context, conversation_history)
            else:
                return self._generate_simple(query, context)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error. Please contact support at 0320-1007448."
    
    def _clean_context(self, context: str) -> str:
        """Strip source tags and formatting for a cleaner prompt"""
        if not context:
            return context
        cleaned = re.sub(r'\[Source \d+: .+? \(Relevance: [\d.]+\)\]', '', context)
        cleaned = re.sub(r'--- Document Snippet \d+.*? ---', '', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        return cleaned
    
    def _generate_with_llm(self, query: str, context: str = None, conversation_history: list = None):
        """Builds advanced prompt and sends to the active provider"""
        prompt = self._build_prompt(query, context, conversation_history)
        
        # Priority: OpenAI
        if os.getenv('OPENAI_API_KEY'):
            print(f"===== SENDING REQUEST TO OPENAI =====")
            return self._generate_with_openai(prompt)
        
        # Priority: Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            print(f"===== SENDING REQUEST TO ANTHROPIC =====")
            return self._generate_with_anthropic(prompt)
        
        return self._generate_simple(query, context)
    
    def _generate_with_openai(self, prompt: str):
        """OpenAI v1.0+ Call with Accuracy tuning"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a professional retail sales manager."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,   # Increased from 50 to allow full lists/policies
                temperature=0.3  # Lowered for higher factual consistency
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            raise
    
    def _generate_with_anthropic(self, prompt: str):
        """Anthropic Call for Claude 3.5 Sonnet"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic error: {str(e)}")
            raise

    def _generate_simple(self, query: str, context: str = None):
        """Simple fallback if APIs are disconnected"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! Welcome to our store. How can I assist you with our 2026 Summer Suits today?"
        return "I'm currently having trouble reaching my database. For immediate help, please contact 0320-1007448."

    def _build_prompt(self, query: str, context: str = None, conversation_history: list = None):
        """High-accuracy prompt engineering (Advanced Level)"""
        
        # 1. System Persona
        prompt = (
            "### ROLE ###\n"
            "You are the Lead Sales Expert for 'Ladies Summer Suits Catalog 2026'. "
            "Provide sophisticated, accurate, and helpful responses based ONLY on provided data.\n\n"
        )

        # 2. Advanced Accuracy Constraints
        prompt += (
            "### STRICT GUIDELINES ###\n"
            "1. NO META-TALK: Never say 'The context mentions' or 'According to the catalog'. Speak naturally as the brand.\n"
            "2. EXHAUSTIVE DATA: If asked for a list (like all colors or all suits), provide EVERY item found in the context. Do not truncate.\n"
            "3. POLICY PRECISION: For refund/exchange queries, quote the specific rules (e.g., 7-day window, 48-hour defect notice).\n"
            "4. FALLBACK: If info is missing, say you don't have that specific detail yet and provide contact: 0320-1007448.\n\n"
        )

        # 3. Inject Context
        if context:
            prompt += f"### TRUSTED PRODUCT DATA ###\n{self._clean_context(context)}\n\n"
        
        # 4. History
        if conversation_history:
            prompt += "### RECENT CONVERSATION ###\n"
            for msg in conversation_history[-2:]:
                role = "Customer" if msg.get('role') == 'user' else "Assistant"
                prompt += f"{role}: {msg.get('content', '')}\n"
            prompt += "\n"

        # 5. Final Task
        prompt += (
            f"### CURRENT CUSTOMER QUERY ###\n{query}\n\n"
            "### RESPONSE STRUCTURE ###\n"
            "- Answer clearly and warmly.\n"
            "- Use bullet points for lists (colors, features, or rules).\n"
            "- End with a helpful follow-up (e.g., 'Shall I help you with the size chart?')."
        )
        
        return prompt