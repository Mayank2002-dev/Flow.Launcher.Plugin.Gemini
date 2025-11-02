#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flox import Flox
import os
import tempfile
import csv

class Gemini(Flox):
    """Flow Launcher plugin for Google Gemini AI"""
    
    def __init__(self):
        super().__init__()
        self.icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "Images", 
            "app.png"
        )
        self.gemini_api = None
        self.conversation_history = []
        self.last_response = ""
    
    def query(self, query):
        """Handle query from Flow Launcher"""
        try:
            # Import here to avoid issues at startup
            from gemini_api import GeminiAPI
            
            # Get settings from Flox
            api_key = self.settings.get("api_key", "")
            prompt_stop = self.settings.get("prompt_stop", "||")
            
            # Check if API key is set
            if not api_key:
                self.add_item(
                    title="Please set your Gemini API key",
                    subtitle="Go to Settings > Plugins > Gemini to configure",
                    icon=self.icon_path
                )
                return
            
            # Check if query ends with stop keyword
            if not query.endswith(prompt_stop):
                self.add_item(
                    title=f"Type your prompt and end with '{prompt_stop}' to submit",
                    subtitle=f"Example: what is AI? {prompt_stop}",
                    icon=self.icon_path
                )
                return
            
            # Remove stop keyword from query
            query = query[:-len(prompt_stop)].strip()
            
            if not query:
                self.add_item(
                    title="Please enter a prompt",
                    subtitle=f"Type your question before {prompt_stop}",
                    icon=self.icon_path
                )
                return
            
            # Parse system prompt keyword
            system_prompt = self.get_system_prompt(query)
            if system_prompt:
                # Remove the keyword from the query
                words = query.split()
                query = " ".join(words[1:])
            
            # Initialize Gemini API if needed
            if not self.gemini_api:
                self.gemini_api = GeminiAPI(self.settings)
            
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
            self.add_item(
                title="Response from Gemini",
                subtitle=response[:100] + "..." if len(response) > 100 else response,
                icon=self.icon_path,
                method=self.show_full_response,
                parameters=[]
            )
            
            self.add_item(
                title="Copy to clipboard",
                subtitle="Copy the full response to clipboard",
                icon=self.icon_path,
                method=self.copy_to_clipboard,
                parameters=[]
            )
            
            self.add_item(
                title="Open in text file",
                subtitle="Open the response in a new text file",
                icon=self.icon_path,
                method=self.open_in_file,
                parameters=[]
            )
            
            if self.settings.get("save_conversation") == "true":
                self.add_item(
                    title="Clear conversation history",
                    subtitle="Start a new conversation",
                    icon=self.icon_path,
                    method=self.clear_history,
                    parameters=[]
                )
            
        except Exception as e:
            self.add_item(
                title="Error",
                subtitle=str(e),
                icon=self.icon_path
            )
    
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
        self.add_item(
            title=self.last_response,
            subtitle="Full response from Gemini (click to copy)",
            icon=self.icon_path,
            method=self.copy_to_clipboard,
            parameters=[]
        )
    
    def copy_to_clipboard(self):
        """Copy response to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(self.last_response)
            self.add_item(
                title="Copied!",
                subtitle="Response copied to clipboard",
                icon=self.icon_path
            )
        except Exception as e:
            self.add_item(
                title="Error",
                subtitle=f"Failed to copy: {str(e)}",
                icon=self.icon_path
            )
    
    def open_in_file(self):
        """Open response in a text file"""
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(self.last_response)
                temp_path = f.name
            
            # Open file with default text editor
            os.startfile(temp_path)
            
            self.add_item(
                title="Opened!",
                subtitle="Response opened in text file",
                icon=self.icon_path
            )
        except Exception as e:
            self.add_item(
                title="Error",
                subtitle=f"Failed to open file: {str(e)}",
                icon=self.icon_path
            )
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.add_item(
            title="Cleared!",
            subtitle="Conversation history cleared",
            icon=self.icon_path
        )

if __name__ == "__main__":
    Gemini()