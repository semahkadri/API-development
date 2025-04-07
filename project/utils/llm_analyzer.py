"""Utility module for analyzing text using Google's Gemini API for semantic analysis."""

from typing import Dict, List, Optional
import google.generativeai as genai
import logging
import config

logger = logging.getLogger(__name__)

# Configure Gemini API key
genai.configure(api_key=config.GEMINI_API_KEY)

def analyze_with_llm(text_data: List[str]) -> Dict[str, List[str]]:
    """Perform semantic analysis on text data using Google's Gemini API to extract skills, experiences, and qualifications.

    Args:
        text_data: List of text strings from job descriptions or CVs.

    Returns:
        Dictionary containing semantically extracted skills, experiences, and qualifications, or empty lists on failure.
    """
    try:
        all_text = " ".join(text_data)
        prompt = config.LLM_ANALYSIS_PROMPT.format(text=all_text)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        extracted_text = response.text.strip()
        skills, experiences, qualifications = [], [], []
        lines = extracted_text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("Skills:"):
                current_section = "skills"
                skills = line.replace("Skills:", "").strip().split(", ")
            elif line.startswith("Experiences:"):
                current_section = "experiences"
                experiences = line.replace("Experiences:", "").strip().split(", ")
            elif line.startswith("Qualifications:"):
                current_section = "qualifications"
                qualifications = line.replace("Qualifications:", "").strip().split(", ")
            elif line and current_section:
                if current_section == "skills":
                    skills.extend(line.split(", "))
                elif current_section == "experiences":
                    experiences.extend(line.split(", "))
                elif current_section == "qualifications":
                    qualifications.extend(line.split(", "))

        # Clean and deduplicate results
        skills = list(set(skill.strip() for skill in skills if skill.strip()))
        experiences = list(set(exp.strip() for exp in experiences if exp.strip()))
        qualifications = list(set(qual.strip() for qual in qualifications if qual.strip()))

        logger.info("Gemini LLM semantic analysis completed successfully")
        return {
            "skills": skills,
            "experiences": experiences,
            "qualifications": qualifications
        }
    except Exception as e:
        logger.error(f"Error during Gemini LLM semantic analysis: {str(e)}")
        return {"skills": [], "experiences": [], "qualifications": []}