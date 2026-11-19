"""Юніт-тести модуля agile_metrics (PyTest).

Нормальні випадки перевіряються на даних із лабораторних робіт 1–3,
окремо – граничні значення та некоректний ввід.
"""
import math

import pytest

from agile_metrics import (
    Task,
    average,
    cycle_time,
    lead_time,
    little_wait,
    priority,
    select_sprint,
    sprints_needed,
    team_capacity,
    velocity,
)

# Product Backlog застосунку нагадування про ліки з ЛР1 (у порядку пріоритету)
LR1_BACKLOG = [
    Task("MR-1", 2),
    Task("MR-2", 5, ("MR-1",)),
    Task("MR-3", 3, ("MR-1",)),
    Task("MR-4", 3, ("MR-2", "MR-3")),
    Task("MR-5", 3, ("MR-1",)),
    Task("MR-6", 2, ("MR-4", "MR-5")),
    Task("MR-7", 1, ("MR-1",)),
    Task("MR-8", 5, ("MR-2",)),
    Task("MR-9", 5, ("MR-4", "MR-7")),
    Task("MR-10", 3, ("MR-8",)),
    Task("MR-11", 3, ("MR-9",)),
    Task("MR-12", 2, ("MR-8",)),
]


# ---------- team_capacity ----------
class TestTeamCapacity:
    def test_lab1_capacity(self):
        # ЛР1 і ЛР2: 3 учасники, 10 днів, k = 0,7
        assert team_capacity(3, 10, 0.7) == 21.0

    @pytest.mark.parametrize(
        "members, days, focus, expected",
        [(1, 1, 1.0, 1.0), (5, 5, 0.6, 15.0), (1, 10, 0.01, 0.1), (7, 20, 1, 140.0)],
    )
    def test_valid_values(self, members, days, focus, expected):
        assert team_capacity(members, days, focus) == expected

    @pytest.mark.parametrize("focus", [0, -0.1, 1.01, 2])
    def test_focus_out_of_range(self, focus):
        with pytest.raises(ValueError):
            team_capacity(3, 10, focus)

    @pytest.mark.parametrize("members, days", [(0, 10), (-1, 10), (3, 0), (3, -5)])
    def test_non_positive_members_or_days(self, members, days):
        with pytest.raises(ValueError):
            team_capacity(members, days, 0.7)

    @pytest.mark.parametrize("members", [2.5, "3", None, True])
    def test_wrong_type_members(self, members):
        with pytest.raises(TypeError):
            team_capacity(members, 10, 0.7)

    @pytest.mark.parametrize("focus", ["0.7", None, False])
    def test_wrong_type_focus(self, focus):
        with pytest.raises(TypeError):
            team_capacity(3, 10, focus)

    @pytest.mark.parametrize("focus", [math.nan, math.inf])
    def test_focus_nan_inf(self, focus):
        with pytest.raises(ValueError):
            team_capacity(3, 10, focus)


# ---------- priority ----------
class TestPriority:
    @pytest.mark.parametrize(
        "story, value, sp, expected",
        [("US-1", 9, 5, 1.8), ("US-2", 8, 3, 2.67), ("US-3", 10, 5, 2.0),
         ("US-5", 9, 3, 3.0), ("US-8", 8, 8, 1.0), ("US-15", 3, 2, 1.5)],
    )
    def test_lab2_values(self, story, value, sp, expected):
        assert priority(value, sp) == expected, story

    def test_boundaries(self):
        assert priority(1, 13) == 0.08
        assert priority(10, 1) == 10.0

    @pytest.mark.parametrize("value, sp", [(0, 3), (11, 3), (5, 0), (5, -2)])
    def test_out_of_range(self, value, sp):
        with pytest.raises(ValueError):
            priority(value, sp)

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            priority(5, 2.5)


# ---------- sprints_needed ----------
class TestSprintsNeeded:
    def test_lab2_forecast(self):
        # ЛР2: залишок 36 SP при velocity 18 SP -> 2 спринти
        assert sprints_needed(36, 18) == 2

    @pytest.mark.parametrize(
        "remaining, vel, expected",
        [(0, 18, 0), (1, 18, 1), (18, 18, 1), (19, 18, 2), (37, 18, 3), (10.5, 3.5, 3)],
    )
    def test_rounding_up(self, remaining, vel, expected):
        assert sprints_needed(remaining, vel) == expected

    @pytest.mark.parametrize("remaining, vel", [(-1, 18), (36, 0), (36, -18)])
    def test_invalid(self, remaining, vel):
        with pytest.raises(ValueError):
            sprints_needed(remaining, vel)

    def test_wrong_type(self):
        with pytest.raises(TypeError):
            sprints_needed("36", 18)


# ---------- velocity ----------
class TestVelocity:
    def test_lab2_sprint1(self):
        # US-1, US-2, US-9, US-3 прийнято, US-5 не завершено -> 18 SP
        stories = [(5, True), (3, True), (5, True), (5, True), (3, False)]
        assert velocity(stories) == 18

    def test_empty_and_nothing_done(self):
        assert velocity([]) == 0
        assert velocity([(5, False), (3, False)]) == 0

    def test_invalid_sp(self):
        with pytest.raises(ValueError):
            velocity([(0, True)])

    def test_invalid_done_flag(self):
        with pytest.raises(TypeError):
            velocity([(3, "yes")])


# ---------- select_sprint ----------
class TestSelectSprint:
    def test_lab1_sprint1(self):
        # ЛР1: при ємності 21 SP у спринт потрапляють MR-1…MR-7 на 19 SP
        chosen = select_sprint(LR1_BACKLOG, 21)
        assert [t.key for t in chosen] == [f"MR-{i}" for i in range(1, 8)]
        assert sum(t.sp for t in chosen) == 19

    def test_dependency_not_in_sprint_is_skipped(self):
        # MR-12 (2 SP) вміщується в залишок, але залежить від MR-8, якого немає в спринті
        chosen = {t.key for t in select_sprint(LR1_BACKLOG, 21)}
        assert "MR-12" not in chosen

    def test_whole_backlog_fits(self):
        assert len(select_sprint(LR1_BACKLOG, 37)) == 12

    def test_zero_capacity(self):
        assert select_sprint(LR1_BACKLOG, 0) == []

    def test_empty_backlog(self):
        assert select_sprint([], 21) == []

    def test_exact_fit(self):
        backlog = [Task("A", 3), Task("B", 2, ("A",))]
        assert [t.key for t in select_sprint(backlog, 5)] == ["A", "B"]

    def test_unknown_dependency(self):
        with pytest.raises(ValueError, match="невідомих"):
            select_sprint([Task("A", 3, ("Z",))], 10)

    def test_self_dependency(self):
        with pytest.raises(ValueError, match="сам від себе"):
            select_sprint([Task("A", 3, ("A",))], 10)

    def test_duplicate_keys(self):
        with pytest.raises(ValueError, match="однаковими"):
            select_sprint([Task("A", 3), Task("A", 2)], 10)

    def test_negative_capacity(self):
        with pytest.raises(ValueError):
            select_sprint(LR1_BACKLOG, -1)


class TestTask:
    @pytest.mark.parametrize("key", ["", "   "])
    def test_empty_key(self, key):
        with pytest.raises(ValueError):
            Task(key, 3)

    def test_bad_sp(self):
        with pytest.raises(ValueError):
            Task("A", 0)
        with pytest.raises(TypeError):
            Task("A", 2.5)


# ---------- lead / cycle time, Little ----------
class TestFlowMetrics:
    def test_lead_and_cycle_time(self):
        assert lead_time(2, 10) == 8
        assert cycle_time(5, 10) == 5

    def test_same_day(self):
        assert lead_time(3, 3) == 0
        assert cycle_time(0, 0) == 0

    def test_done_before_start(self):
        with pytest.raises(ValueError, match="раніше"):
            cycle_time(7, 5)

    def test_negative_day(self):
        with pytest.raises(ValueError):
            lead_time(-1, 5)

    def test_wrong_type_day(self):
        with pytest.raises(TypeError):
            cycle_time(1.5, 4)

    def test_average(self):
        assert average([6, 7, 8]) == 7.0
        assert average([8.22]) == 8.22

    def test_average_empty(self):
        with pytest.raises(ValueError):
            average([])

    def test_little_lab3(self):
        # ЛР3: ліміт Review/Testing 2 задачі, тестувальник ~1,1 задачі на день -> ~1,8 дня
        assert little_wait(2, 1.1) == pytest.approx(1.82)

    def test_little_zero_wip(self):
        assert little_wait(0, 1.1) == 0.0

    @pytest.mark.parametrize("wip, thr", [(-1, 1), (2, 0), (2, -1)])
    def test_little_invalid(self, wip, thr):
        with pytest.raises(ValueError):
            little_wait(wip, thr)
