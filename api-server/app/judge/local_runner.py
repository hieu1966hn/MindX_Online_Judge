"""
Local runner implementation using subprocess.
NOTE: This runner is for MVP/local development only. 
It does NOT have strong security sandboxing.
"""
import subprocess
import time
import os
import tempfile
from pathlib import Path

from app.judge.base import BaseRunner, JudgeResult, JudgeStatus


class LocalRunner(BaseRunner):
    """
    Runs code locally using subprocess.Popen.
    Supports Python 3 by default.
    """

    def run(
        self,
        source_code: str,
        language: str,
        input_data: str,
        time_limit_ms: int,
        memory_limit_mb: int
    ) -> JudgeResult:
        if language.lower() not in ["python", "python3"]:
            return JudgeResult(
                status=JudgeStatus.SYSTEM_ERROR,
                message=f"Language '{language}' not supported by LocalRunner"
            )

        # Create temporary file for source code
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(source_code)
            temp_file_path = f.name

        try:
            start_time = time.perf_counter()
            
            # Execute code
            # Note: We don't enforce memory limit in this simple MVP runner
            process = subprocess.Popen(
                ["python3", temp_file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(
                    input=input_data, 
                    timeout=time_limit_ms / 1000.0
                )
                
                execution_time = int((time.perf_counter() - start_time) * 1000)
                
                if process.returncode == 0:
                    return JudgeResult(
                        status=JudgeStatus.ACCEPTED, # Placeholder, will be verified against expected output
                        time_ms=execution_time,
                        stdout=stdout,
                        stderr=stderr
                    )
                else:
                    return JudgeResult(
                        status=JudgeStatus.RUNTIME_ERROR,
                        time_ms=execution_time,
                        stdout=stdout,
                        stderr=stderr,
                        message=f"Exit code: {process.returncode}"
                    )

            except subprocess.TimeoutExpired:
                process.kill()
                return JudgeResult(
                    status=JudgeStatus.TIME_LIMIT_EXCEEDED,
                    time_ms=time_limit_ms,
                    message="Time limit exceeded"
                )

        except Exception as e:
            return JudgeResult(
                status=JudgeStatus.SYSTEM_ERROR,
                message=str(e)
            )
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
