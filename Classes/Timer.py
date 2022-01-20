#   _______ _____ __  __ ______ _____     _____ _                _____ _____
#  |__   __|_   _|  \/  |  ____|  __ \   / ____| |        /\    / ____/ ____|
#     | |    | | | \  / | |__  | |__) | | |    | |       /  \  | (___| (___
#     | |    | | | |\/| |  __| |  _  /  | |    | |      / /\ \  \___ \\___ \
#     | |   _| |_| |  | | |____| | \ \  | |____| |____ / ____ \ ____) |___) |
#     |_|  |_____|_|  |_|______|_|  \_\  \_____|______/_/    \_\_____/_____/


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
        return str(self._t)