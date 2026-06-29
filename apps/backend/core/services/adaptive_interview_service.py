from typing import Dict, Any, Optional

class AdaptiveInterviewService:
    """
    Manages the deterministic Question Library.
    Generates parameterized multiple-choice questions when possible.
    """
    
    # Deterministic templates to minimize LLM usage and maximize consistency
    QUESTION_LIBRARY = {
        "medication_adherence": {
            "template": "We noticed you haven't logged your {medication} recently. Have you been taking it?",
            "options": ["Yes, exactly as prescribed", "Yes, but I missed a few doses", "No, I stopped taking it", "I ran out"]
        },
        "missing_lab": {
            "template": "It's been a while since we received a {lab_type} report. Do you have a recent one to upload?",
            "options": ["Yes, I will upload it now", "No, I need to schedule a test", "My doctor said I don't need it yet"]
        },
        "symptom_progression": {
            "template": "You recently mentioned {symptom}. How is it feeling now compared to before?",
            "options": ["Much better", "About the same", "Slightly worse", "Much worse"]
        }
    }

    def generate_question(self, domain: str, context_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Attempts to pull a question from the library. 
        If it fails, it can fallback to an LLM, but we strictly prefer the library.
        """
        if domain in self.QUESTION_LIBRARY:
            q_template = self.QUESTION_LIBRARY[domain]
            try:
                text = q_template["template"].format(**context_vars)
                return {
                    "question_text": text,
                    "type": "MCQ",
                    "options": q_template["options"]
                }
            except KeyError:
                # Missing context var, fallback
                pass
                
        # LLM Fallback (mocked for this implementation, would call LLMProvider)
        return {
            "question_text": f"Could you provide an update regarding {domain}?",
            "type": "OPEN",
            "options": []
        }
