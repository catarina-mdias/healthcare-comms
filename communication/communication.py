from abc import ABC, abstractmethod
from typing import Dict, List

from communication.schema import CommunicationUseCase


class Communication(ABC):
    def __init__(self, use_case: CommunicationUseCase) -> None:
        self.use_case = use_case

    @abstractmethod
    async def get_communication(self, **kwargs) -> Dict:
        raise NotImplementedError

    @abstractmethod
    async def act_on_communication_result(
        self,
        was_successful: bool,
        high_success_examples_id: List[int],
        low_success_examples_id: List[int],
    ) -> None:
        raise NotImplementedError
