"""
database/models.py

Data classes for structured representation of candidates and analyses.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Candidate:
    id: Optional[int] = None
    name: str = "Unknown"
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    ats_score: float = 0.0
    prediction: str = "Other"
    match_score: float = 0.0
    missing_skills: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    job_description: str = ""
    filename: str = ""
    session_id: str = ""

    def to_dict(self):
        """Convert to dictionary for easier session storage or JSON responses."""
        return self.__dict__