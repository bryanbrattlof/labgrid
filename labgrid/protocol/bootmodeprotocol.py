
import abc

class BootModeProtocol(abc.ABC):

    @abc.abstractmethod
    def set(self, mode: int) -> None:
        """set the devstat (boodmode) on the device"""
        raise NotImplementedError
