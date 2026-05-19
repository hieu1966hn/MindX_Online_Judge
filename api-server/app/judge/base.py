"""
Base classes and interfaces for Judge runners.
"""
import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


class JudgeStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILE_ERROR = "compile_error"
    SYSTEM_ERROR = "system_error"


@dataclass
class JudgeResult:
    """Detailed result of a single test case or full submission."""
    status: JudgeStatus
    score: float = 0.0
    time_ms: int = 0
    memory_mb: float = 0.0
    message: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class BaseRunner(ABC):
    """
    Interface for code execution runners.
    Can be implemented via Subprocess, Docker, or external API.
    """
    
    @abstractmethod
    def run(
        self, 
        source_code: str, 
        language: str, 
        input_data: str,
        time_limit_ms: int,
        memory_limit_mb: int
    ) -> JudgeResult:
        """Execute source code with given input and limits."""
        pass
