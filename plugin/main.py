#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flox import Flox
import os
import tempfile
import csv
from plugin.gemini_api import GeminiAPI
from plugin.settings import Settings

class Gemini(Flox):
    """Flow Launcher plugin for Google Gemini AI"""
    
    def __init__(self):
        super().__init__()
        self.icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "Images", 
            "app.png"
        )
        self.settings = Settings(self.settings_path)
        self.gemini_api = None
        self.conversation_history = []
        self.last_response = ""
        
    def query(self, query):
        """Handle query from Flow Launcher"""
        try:
            # Get settings
            api_key = self.settings.get("api_key", "")
            prompt_stop = self.settings.get("prompt_stop", "||")
            
            # Check if API key is set
            if not api_key:
                return self.show_error("Please set your Gemini API key in settings")
            
            # Check if query ends with stop keyword
            if not query.endswith(prompt_stop):
                return self.show_message(
                    f"Type your prompt and end with '{prompt_stop}' to submit",
                    "Example: what is AI? {prompt_stop}".replace("{prompt_stop}", prompt_stop)
                )
            
            # Remove stop keyword from query
            query = query[:-len(prompt_stop)].strip()
            
            # Parse system prompt keyword
            system_prompt = self.get_system_prompt(query)
            if system_prompt:
                # Remove the keyword from the query
                words = query.split()
                query = " ".join(words[1:])
            
            # Initialize Gemini API if needed
            if not self.gemini_api:
                self.gemini_api = GeminiAPI(self.settings)
            
            # Show loading message
            results = [self.show_loading()]
            
            # Get response from Gemini
            response = self.gemini_api.get_response(
                query, 
                system_prompt=system_prompt,
                conversation_history=self.conversation_history if self.settings.get("save_conversation") == "true" else None
            )
            
            # Save conversation if enabled
            if self.settings.get("save_conversation") == "true":
                self.conversation_history.append({"role": "user", "parts": [query]})
                self.conversation_history.append({"role": "model", "parts": [response]})
            
            # Store the response
            self.last_response = response
            
            # Return results with actions
            results = [
                {
                    "Title": "Response from Gemini",
                    "SubTitle": response[:100] + "..." if len(response) > 100 else response,
                    "IcoPath": self.icon_path,
                    "JsonRPCAction": {
                        "method": "show_full_response",
                        "parameters": []
                    }
                },
                {
                    "Title": "Copy to clipboard",
                    "SubTitle": "Copy the full response to clipboard",
                    "IcoPath": self.icon_path,
                    "JsonRPCAction": {
                        "method": "copy_to_clipboard",
                        "parameters": []
                    }
                },
                {
                    "Title": "Open in text file",
                    "SubTitle": "Open the response in a new text file",
                    "IcoPath": self.icon_path,
                    "JsonRPCAction": {
                        "method": "open_in_file",
                        "parameters": []
                    }
                }
            ]
            
            if self.settings.get("save_conversation") == "true":
                results.append({
                    "Title": "Clear conversation history",
                    "SubTitle": "Start a new conversation",
                    "IcoPath": self.icon_path,
                    "JsonRPCAction": {
                        "method": "clear_history",
                        "parameters": []
                    }
                })
            
            return results
            
        except Exception as e:
            return self.show_error(f"Error: {str(e)}")
    
    def get_system_prompt(self, query):
        """Get system prompt based on keyword in query"""
        try:
            words = query.split()
            if not words:
                keyword = self.settings.get("default_prompt", "normal")
            else:
                keyword = words[0].lower()
            
            # Read system messages CSV
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "system_messages.csv"
            )
            
            if not os.path.exists(csv_path):
                return None
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Keyword'].lower() == keyword:
                        return row['System Message']
            
            # If no match found and not the first word, use default
            if len(words) > 1:
                default_keyword = self.settings.get("default_prompt", "normal")
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['Keyword'].lower() == default_keyword:
                            return row['System Message']
            
            return None
            
        except Exception:
            return None
    
    def show_full_response(self):
        """Show full response in Flow Launcher"""
        return [
            {
                "Title": self.last_response,
                "SubTitle": "Full response from Gemini",
                "IcoPath": self.icon_path,
                "JsonRPCAction": {
                    "method": "copy_to_clipboard",
                    "parameters": []
                }
            }
        ]
    
    def copy_to_clipboard(self):
        """Copy response to clipboard"""
        import pyperclip
        pyperclip.copy(self.last_response)
        return [self.show_message("Copied!", "Response copied to clipboard")]
    
    def open_in_file(self):
        """Open response in a text file"""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(self.last_response)
                temp_path = f.name
            
            # Open file with default text editor
            os.startfile(temp_path)
            
            return [self.show_message("Opened!", "Response opened in text file")]
        except Exception as e:
            return self.show_error(f"Error opening file: {str(e)}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return [self.show_message("Cleared!", "Conversation history cleared")]
    
    def show_error(self, message):
        """Show error message"""
        return [
            {
                "Title": "Error",
                "SubTitle": message,
                "IcoPath": self.icon_path
            }
        ]
    
    def show_message(self, title, subtitle):
        """Show a message"""
        return {
            "Title": title,
            "SubTitle": subtitle,
            "IcoPath": self.icon_path
        }
    
    def show_loading(self):
        """Show loading message"""
        return {
            "Title": "Loading...",
            "SubTitle": "Waiting for Gemini response",
            "IcoPath": self.icon_path
        }

if __name__ == "__main__":
    Gemini()