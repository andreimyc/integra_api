import random
import string


def assert_has_keys(obj: dict, keys: list[str]) -> None:
    for key in keys:
        assert key in obj, f"Отсутствует обязательное поле {key} в объекте: {obj}"


def random_suffix(length: int = 4) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


