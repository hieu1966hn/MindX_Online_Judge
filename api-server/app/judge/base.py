# TODO: implement in task 7.1
from abc import ABC, abstractmethod


class AbstractJudgeRunner(ABC):
    @abstractmethod
    def judge(self, submission) -> None:
        """Judge a submission and update its verdict in the database."""
        ...
