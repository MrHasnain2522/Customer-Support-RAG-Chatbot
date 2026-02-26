"""
Response Generator - Generates responses using LLM
Fixed:
  1. OpenAI Client initialization (removed potential proxy conflicts)
  2. Updated Anthropic model to claude-3-5-sonnet-20241022
  3. Added High-Performance 10/10 Accuracy Prompting
  4. Added comprehensive debug logging
"""
import os
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """Generator for creating responses"""
    
    def __init__(self):
        """Initialize generator"""
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.use_llm = bool(self.api_key)
        
        print("\n===== GENERATOR INIT DEBUG =====")
        print(f"API KEY FOUND: {self.use_llm}")
        print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")
        print(f"ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not Set'}")
        print("================================\n")

        if not self.use_llm:
            logger.warning("No API key found. Using simple responses.")
        else:
            logger.info(f"ResponseGenerator initialized. LLM enabled: {self.use_llm}")
    
    def generate(self, query: str, context: str = None, conversation_history: list = None):
        """Generate response with debug tracking"""
        try:
            print(f"\n========== GENERATE DEBUG ==========")
            print(f"QUERY: {query}")
            if context:
                print(f"CONTEXT PREVIEW: {context[:150]}...")
            print(f"USE LLM: {self.use_llm}")
            print(f"====================================\n")

            if self.use_llm:
                return self._generate_with_llm(query, context, conversation_history)
            else:
                return self._generate_simple(query, context)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error. Please try again."
    
    def _clean_context(self, context: str) -> str:
        """Strip source citation tags from context"""
        if not context:
            return context
        cleaned = re.sub(r'\[Source \d+: .+? \(Relevance: [\d.]+\)\]', '', context)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        return cleaned
    
    def _generate_with_llm(self, query: str, context: str = None, conversation_history: list = None):
        """Generate using LLM API"""
        try:
            prompt = self._build_prompt(query, context, conversation_history)
            
            # Try OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                print(f"===== SENDING REQUEST TO OPENAI =====")
                print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
                print(f"======================================")
                return self._generate_with_openai(prompt)
            
            # Try Anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                print(f"===== SENDING REQUEST TO ANTHROPIC =====")
                print(f"=========================================")
                return self._generate_with_anthropic(prompt)
            
            return self._generate_simple(query, context)
            
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return self._generate_simple(query, context)
    
    def _generate_with_openai(self, prompt: str):
        """Generate using OpenAI v1.0+ with Proxy Fix"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "system", "content": "You are a professional retail assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.9  # Lower temperature for higher accuracy/consistency
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
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
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
            return "Hello! Welcome to our store. How can I assist you today?"
        return "I'm sorry, I'm having trouble reaching my database. Please ask about our summer suits or contact support at adsab2522@gmail.com."

    def _build_prompt(self, query: str, context: str = None, conversation_history: list = None):
        """High-accuracy prompt engineering for 10/10 performance"""
        
        # 1. System Persona & Identity
        prompt = (
            "### ROLE ###\n"
            "You are a Senior Sales Expert for 'Ladies Summer Suits Catalog 2026'. "
            "Your personality is helpful, sophisticated, and retail-oriented. "
            "You must provide accurate information based ONLY on the provided catalog data.\n\n"
        )

        # 2. Constraints (The "Secret Sauce" for Accuracy)
        prompt += (
            "### STRICT RULES ###\n"
            "1. NEVER mention 'Based on the context' or 'According to the document'. Speak naturally.\n"
            "2. If the answer is not in the PRODUCT CONTEXT, politely say you don't have that specific info and offer to help with suit selections.\n"
            "3. If a price or material is mentioned in context, use it. Do not guess.\n"
            "4. Keep responses under 80 words to ensure customer engagement.\n"
            "5. If the customer is just saying 'Hi', greet them warmly and mention 1-2 popular categories like Lawn or Chiffon suits.\n\n"
        )

        # 3. Context Injection
        if context:
            prompt += f"### PRODUCT CONTEXT (TRUSTED DATA) ###\n{self._clean_context(context)}\n\n"
        
        # 4. Conversation Thread
        if conversation_history:
            prompt += "### CONVERSATION HISTORY ###\n"
            for msg in conversation_history[-3:]:
                role = "Customer" if msg.get('role') == 'user' else "Assistant"
                prompt += f"{role}: {msg.get('content', '')}\n"
            prompt += "\n"

        # 5. Final Task Instructions
        prompt += (
            f"### CURRENT CUSTOMER QUERY ###\n{query}\n\n"
            "### RESPONSE STRUCTURE ###\n"
            "- Acknowledge the query warmly.\n"
            "- Provide 2-3 specific product features (fabric, delivery time, or price).\n"
            "- End with a personalized follow-up question (e.g., 'Would you like to see our color options for this suit?')."
        )
        
        return prompt