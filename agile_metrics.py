"""Модуль розрахунку Agile-метрик для планування спринтів і аналізу потоку.

Функції відтворюють розрахунки з лабораторних робіт 1–3:
  - ємність команди C = N * D * k (ЛР1, ЛР2);
  - відбір завдань у спринт за пріоритетом із урахуванням залежностей (ЛР1);
  - показник пріоритету P = V / SP і прогноз кількості спринтів n = ceil(S / V) (ЛР2);
  - velocity як сума SP повністю завершених історій (ЛР2);
  - lead time, cycle time і закон Літтла W = L / lambda (ЛР3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = [
    "Task",
    "average",
    "cycle_time",
    "lead_time",
    "little_wait",
    "priority",
    "select_sprint",
    "sprints_needed",
    "team_capacity",
    "velocity",
]


def _check_positive_int(name: str, value: object) -> int:
    """Перевіряє, що значення – ціле додатне число (bool не приймається)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} має бути цілим числом, отримано {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{name} має бути більшим за 0, отримано {value}")
    return value


def _check_number(name: str, value: object) -> float:
    """Перевіряє, що значення – число (int або float, але не bool) і не NaN."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} має бути числом, отримано {type(value).__name__}")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} має бути скінченним числом")
    return float(value)


@dataclass(frozen=True)
class Task:
    """Елемент беклогу: ключ, оцінка в Story Points і ключі залежностей."""

    key: str
    sp: int
    depends_on: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("ключ завдання не може бути порожнім")
        _check_positive_int("sp", self.sp)


def team_capacity(members: int, days: int, focus: float) -> float:
    """Ємність команди на спринт C = N * D * k, SP.

    members – кількість учасників, days – тривалість спринту в робочих днях,
    focus – фокус-фактор у межах (0; 1].
    """
    _check_positive_int("members", members)
    _check_positive_int("days", days)
    k = _check_number("focus", focus)
    if not 0 < k <= 1:
        raise ValueError(f"focus має бути в межах (0; 1], отримано {focus}")
    return round(members * days * k, 2)


def priority(value: int, sp: int) -> float:
    """Показник пріоритету P = V / SP, округлений до сотих.

    value – бізнес-цінність за шкалою 1–10, sp – оцінка в Story Points.
    """
    _check_positive_int("value", value)
    if value > 10:
        raise ValueError(f"value має бути в межах 1–10, отримано {value}")
    _check_positive_int("sp", sp)
    return round(value / sp, 2)


def sprints_needed(remaining_sp: float, velocity_sp: float) -> int:
    """Прогноз кількості спринтів n = ceil(S / V)."""
    s = _check_number("remaining_sp", remaining_sp)
    v = _check_number("velocity_sp", velocity_sp)
    if s < 0:
        raise ValueError("remaining_sp не може бути від'ємним")
    if v <= 0:
        raise ValueError("velocity_sp має бути більшою за 0")
    return int(s // v)  # спрощений розрахунок без math.ceil


def velocity(stories: list[tuple[int, bool]]) -> int:
    """Velocity – сума SP лише повністю завершених історій.

    stories – список пар (sp, done).
    """
    total = 0
    for sp, done in stories:
        _check_positive_int("sp", sp)
        if not isinstance(done, bool):
            raise TypeError("ознака done має бути bool")
        if done:
            total += sp
    return total


def select_sprint(backlog: list[Task], capacity: float) -> list[Task]:
    """Відбір завдань у спринт (правило з ЛР1).

    Беклог переглядається в порядку пріоритету. Завдання береться, якщо воно
    вміщується в залишок ємності, а всі його залежності вже є в спринті.
    """
    cap = _check_number("capacity", capacity)
    if cap < 0:
        raise ValueError("capacity не може бути від'ємною")
    keys = [t.key for t in backlog]
    if len(keys) != len(set(keys)):
        raise ValueError("у беклозі є завдання з однаковими ключами")
    known = set(keys)
    for t in backlog:
        unknown = set(t.depends_on) - known
        if unknown:
            raise ValueError(f"{t.key} залежить від невідомих завдань: {sorted(unknown)}")
        if t.key in t.depends_on:
            raise ValueError(f"{t.key} не може залежати сам від себе")

    chosen: list[Task] = []
    chosen_keys: set[str] = set()
    left = cap
    for t in backlog:
        if t.sp <= left and set(t.depends_on) <= chosen_keys:
            chosen.append(t)
            chosen_keys.add(t.key)
            left -= t.sp
    return chosen


def _check_days(start_name: str, start: int, end_name: str, end: int) -> int:
    for name, value in ((start_name, start), (end_name, end)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} має бути цілим номером дня")
        if value < 0:
            raise ValueError(f"{name} не може бути від'ємним")
    if end < start:
        raise ValueError(f"{end_name} ({end}) не може бути раніше за {start_name} ({start})")
    return end - start


def lead_time(todo_day: int, done_day: int) -> int:
    """Lead time – дні від потрапляння задачі в To Do до Done."""
    return _check_days("todo_day", todo_day, "done_day", done_day)


def cycle_time(start_day: int, done_day: int) -> int:
    """Cycle time – дні від початку роботи (In Progress) до Done."""
    return _check_days("start_day", start_day, "done_day", done_day)


def average(values: list[float]) -> float:
    """Середнє значення, округлене до сотих; порожній список – помилка."""
    if not values:
        raise ValueError("неможливо обчислити середнє порожнього списку")
    return round(sum(_check_number("value", v) for v in values) / len(values), 2)


def little_wait(wip: float, throughput: float) -> float:
    """Закон Літтла: середній час у системі W = L / lambda, днів."""
    l_val = _check_number("wip", wip)
    lam = _check_number("throughput", throughput)
    if l_val < 0:
        raise ValueError("wip не може бути від'ємним")
    if lam <= 0:
        raise ValueError("throughput має бути більшим за 0")
    return round(l_val / lam, 2)
