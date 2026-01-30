import datetime
import random
import time
from typing import Optional


class PollTimer:
    """Utility for making sure the request timeout is not exceeded when polling.

    When polling, there is no persistent connection to the server that can time out. Instead, we
    have to manually keep track of time.
    """

    def __init__(
        self,
        timeout: Optional[datetime.timedelta] = None,
        interval: Optional[datetime.timedelta] = None,
        jitter_factor: float = 0.1,
    ) -> None:
        """Creates a new instance of the `PollTimer` class.

        Args:
            timeout: Maximum time to wait before aborting the RPC.
            interval: Time to wait between polls.
            jitter_factor: Factor for adding random jitter to the interval (0.0 to 1.0).
                A value of 0.1 means the interval can vary by ±10%. Defaults to 0.1.
                Set to 0.0 to disable jitter.
        """
        self._start = time.time()
        self._timeout = timeout or datetime.timedelta(minutes=10)
        self._interval = interval or datetime.timedelta(milliseconds=100)
        self._jitter_factor = max(0.0, min(1.0, jitter_factor))  # Clamp between 0 and 1

    def sleep_interval_or_raise(self) -> float:
        """Returns the time to sleep until the next poll with optional jitter.

        The jitter helps prevent thundering herd problems when many clients
        are polling simultaneously by adding random variation to the interval.

        Returns:
            Time to sleep until the next poll (with jitter applied).

        Raises:
            TimeoutError when the total polling time is used up.
        """
        runtime = time.time() - self._start
        if runtime > self._timeout.total_seconds():
            raise TimeoutError(f"Polling timed out after {runtime} seconds.")

        base_interval = self._interval.total_seconds()

        # Apply jitter: interval * (1 + random(-jitter_factor, +jitter_factor))
        if self._jitter_factor > 0:
            jitter = base_interval * self._jitter_factor * (2 * random.random() - 1)
            interval_with_jitter = max(0.0, base_interval + jitter)
        else:
            interval_with_jitter = base_interval

        return min(self._timeout.total_seconds() - runtime, interval_with_jitter)
