import logging
import time
from typing import Iterator


def backoff(
    exception,
    retry: int = 3,
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10,
    message: dict = {"error": "Ошибка."},
    log=logging.getLogger(__name__),
):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """
    count = 0

    def exp() -> Iterator[float]:
        nonlocal count
        while True:
            t = start_sleep_time * factor**count
            if t < border_sleep_time:
                count += 1
                yield t
            else:
                yield border_sleep_time

    def wrapper(func, *args, **kwargs):
        def inner(*args, **kwargs):
            count = 0
            errt: str = ""
            while True:
                if count >= retry:
                    raise exception(errt)
                try:
                    return func(*args, **kwargs)
                except exception as err:
                    errt = err
                    log.error(message["error"])
                count += 1
                time.sleep(next(exp()))

        return inner

    return wrapper
