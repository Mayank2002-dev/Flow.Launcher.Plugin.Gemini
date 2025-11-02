#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import google.generativeai as genai
import os

class GeminiAPI:
    """Handler for Google Gemini API interactions"""
    
    def __init__(self, settings_dict):
        """Initialize Gemini API with settings dictionary"""
        # Handle both Settings object and dict
        if hasattr(settings_dict, 'get'):
            self.api_key = settings_dict.get("api_key", "")
            self.model_name = settings_dict.get("model", "gemini-2.0-flash-exp")
            self.max_tokens = int(settings_dict.get("max_tokens", "1000"))
            self.temperature = float(settings_dict.get("temperature", "0.7"))
            use_proxy = settings_dict.get("use_proxy", "false")
            proxy_url = settings_dict.get("proxy_url", "")
        else:
            # Fallback to dict access
            self.api_key = settings_dict.get("api_key", "")
            self.model_name = settings_dict.get("model", "gemini-2.0-flash-exp")
            self.max_tokens = int(settings_dict.get("max_tokens", 1000))
            self.temperature = float(settings_dict.get("temperature", 0.7))
            use_proxy = settings_dict.get("use_proxy", False)
            proxy_url = settings_dict.get("proxy_url", "")
        
        # Configure proxy if enabled
        if use_proxy == "true" or use_proxy is True:
            if proxy_url:
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
        
        self.chat = None
    
    def get_response(self, prompt, system_prompt=None, conversation_history=None):
        """Get response from Gemini API"""
        try:
            # Build the full prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            else:
                full_prompt = prompt
            
            # If conversation history is provided, use chat mode
            if conversation_history is not None:
                if not self.chat:
                    self.chat = self.model.start_chat(history=conversation_history)
                response = self.chat.send_message(full_prompt)
            else:
                # Single message mode
                response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle common errors
            if "API_KEY_INVALID" in error_msg or "invalid api key" in error_msg.lower():
                return "Error: Invalid API key. Please check your Gemini API key in settings."
            elif "quota" in error_msg.lower():
                return "Error: API quota exceeded. Please try again later."
            elif "RATE_LIMIT" in error_msg or "rate limit" in error_msg.lower():
                return "Error: Rate limit exceeded. Please wait a moment and try again."
            else:
                return f"Error: {error_msg}"
    
    def reset_chat(self):
        """Reset the chat session"""
        self.chat = None