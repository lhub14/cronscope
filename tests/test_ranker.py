"""Tests for cronscope.ranker."""

import pytest
from cronscope.ranker import rank, RankResult, _categorize


def test_rank_returns_rank_result_instances():
    results = rank(["* * * * *"])
    assert len(results) == 1
    assert isinstance(results[0], RankResult)


def test_rank_assigns_rank_numbers():
    results = rank(["* * * * *", "0 * * * *", "0 0 * * *"])
    ranks = [r.rank for r in results]
    assert ranks == [1, 2, 3]


def test_rank_orders_by_frequency_descending():
    results = rank(["0 0 * * *", "* * * * *", "0 * * * *"])
    assert results[0].expression == "* * * * *"
    assert results[-1].expression == "0 0 * * *"


def test_rank_every_minute_category():
    results = rank(["* * * * *"])
    assert results[0].category == "every-minute"


def test_rank_hourly_category():
    results = rank(["0 * * * *"])
    assert results[0].category == "hourly"


def test_rank_daily_category():
    results = rank(["0 0 * * *"])
    assert results[0].category == "daily"


def test_rank_weekly_category():
    results = rank(["0 0 * * 0"])
    assert results[0].category == "weekly"


def test_rank_skips_invalid_expressions():
    results = rank(["not_a_cron", "* * * * *"])
    assert len(results) == 1
    assert results[0].expression == "* * * * *"


def test_rank_empty_list():
    results = rank([])
    assert results == []


def test_rank_occurrences_per_day_every_minute():
    results = rank(["* * * * *"])
    assert results[0].occurrences_per_day == 1440.0


def test_rank_occurrences_per_day_hourly():
    results = rank(["0 * * * *"])
    assert results[0].occurrences_per_day == 24.0


def test_rank_description_populated():
    results = rank(["* * * * *"])
    assert isinstance(results[0].description, str)
    assert len(results[0].description) > 0


def test_categorize_boundaries():
    assert _categorize(1440.0) == "every-minute"
    assert _categorize(60.0) == "sub-hourly"
    assert _categorize(24.0) == "hourly"
    assert _categorize(1.0) == "daily"
    assert _categorize(0.14) == "weekly"
    assert _categorize(0.0) == "rare"
