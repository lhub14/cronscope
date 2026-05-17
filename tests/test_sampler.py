"""Tests for cronscope.sampler."""

from datetime import datetime

import pytest

from cronscope.sampler import SampleResult, sample


START = datetime(2024, 1, 15, 0, 0, 0)


def test_sample_returns_sample_result():
    result = sample("* * * * *", START, hours=1, n=5)
    assert isinstance(result, SampleResult)


def test_sample_stores_expression():
    result = sample("0 * * * *", START, hours=24, n=5)
    assert result.expression == "0 * * * *"


def test_sample_description_populated():
    result = sample("0 * * * *", START, hours=24, n=5)
    assert len(result.description) > 0


def test_sample_no_description():
    result = sample("0 * * * *", START, hours=24, n=5, include_description=False)
    assert result.description == ""


def test_every_minute_population_is_60_in_one_hour():
    result = sample("* * * * *", START, hours=1, n=5, seed=42)
    assert result.population == 60


def test_sample_size_capped_at_n():
    result = sample("* * * * *", START, hours=1, n=10, seed=0)
    assert result.sample_size == 10
    assert len(result.samples) == 10


def test_sample_size_capped_at_population_when_n_too_large():
    # hourly over 24 h → 24 occurrences; ask for 100
    result = sample("0 * * * *", START, hours=24, n=100, seed=0)
    assert result.sample_size == 24
    assert len(result.samples) == 24


def test_samples_are_datetime_objects():
    result = sample("* * * * *", START, hours=1, n=5, seed=1)
    for s in result.samples:
        assert isinstance(s, datetime)


def test_samples_are_sorted_ascending():
    result = sample("* * * * *", START, hours=2, n=20, seed=7)
    assert result.samples == sorted(result.samples)


def test_samples_within_window():
    from datetime import timedelta
    result = sample("* * * * *", START, hours=3, n=30, seed=3)
    end = START + timedelta(hours=3)
    for s in result.samples:
        assert START <= s < end


def test_seed_produces_deterministic_results():
    r1 = sample("* * * * *", START, hours=2, n=10, seed=99)
    r2 = sample("* * * * *", START, hours=2, n=10, seed=99)
    assert r1.samples == r2.samples


def test_different_seeds_may_differ():
    r1 = sample("* * * * *", START, hours=2, n=10, seed=1)
    r2 = sample("* * * * *", START, hours=2, n=10, seed=2)
    # With 120 occurrences and n=10, different seeds should give different sets
    assert r1.samples != r2.samples


def test_empty_window_returns_empty_samples():
    result = sample("0 12 * * *", START, hours=1, n=5)
    # midnight start, daily at noon → no occurrences in 1 hour
    assert result.population == 0
    assert result.sample_size == 0
    assert result.samples == []


def test_summary_contains_expression():
    result = sample("0 * * * *", START, hours=24, n=3, seed=0)
    s = result.summary()
    assert "0 * * * *" in s


def test_summary_contains_population():
    result = sample("0 * * * *", START, hours=24, n=3, seed=0)
    s = result.summary()
    assert "24" in s
