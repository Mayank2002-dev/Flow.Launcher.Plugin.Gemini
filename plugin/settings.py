#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

class Settings:
    """Manages plugin settings"""
    
    def __init__(self, settings_path):
        """Initialize settings"""
        self.settings_path = settings_path
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")