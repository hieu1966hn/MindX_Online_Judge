# TODO: implement in task 7.2
from app.judge.base import AbstractJudgeRunner


class LocalSubprocessJudgeRunner(AbstractJudgeRunner):
    """
    MVP judge runner — runs code directly on the host using subprocess.
    No sandbox isolation. Suitable for trusted local development only.

    Upgrade path: Replace with DockerSandboxJudgeRunner for production.
    """

    def judge(self, submission) -> None:
        # TODO: implement in task 7.2
        ...
