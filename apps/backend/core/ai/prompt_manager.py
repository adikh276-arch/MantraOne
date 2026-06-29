import os
from pathlib import Path
from typing import Dict, Any
import yaml

class PromptManager:
    """
    Loads versioned Markdown prompts from the file system.
    Parses frontmatter metadata and templates variables.
    """
    def __init__(self, base_path: str = "prompts"):
        # Resolve to absolute path relative to the backend root
        self.base_path = Path(__file__).parent.parent.parent / base_path

    def load_prompt(self, category: str, version_file: str, context: Dict[str, Any]) -> str:
        """
        Loads a prompt, parses metadata, and injects context.
        """
        prompt_path = self.base_path / category / version_file
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse optional YAML frontmatter for metadata (between ---)
        body = content
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2].strip()
                metadata = yaml.safe_load(frontmatter) or {}
                
        # Inject variables
        try:
            formatted_prompt = body.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing context variable {e} for prompt {category}/{version_file}")
            
        return formatted_prompt
