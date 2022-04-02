import time


class Timer:
    def __init__(self, t0=None, t1=None) -> None:
        self._t = time.time()

    def update_time(self) -> None:
        """
        updates the time to the current time
        """
        self._t = time.time()

    def elapsed_time(self) -> float:
        """
        returns the time elapsed since the last update
        :return: time elapsed since the self._t timestamp (t0)
        :rtype: float
        """
        return time.time() - self._t

    def __str__(self) -> str:
        """
        This function is used to return the string representation of the object
        :return: The string representation of the object
        :rtype: str
        """
        return str(self._t)
