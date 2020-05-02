import unittest

from nose.tools import assert_equal, assert_is_not_none

from controller.data_generator import join_demands, generate_simple_demand, scale_demand, demand_to_json, generate_world
from controller.simulation import build_world
from model.product import Product


class TestJoinDemands(unittest.TestCase):
    def setUp(self) -> None:
        self.apple_demand = [{Product(1, 1, 'apple'): 1}] * 2
        self.clam_demand = [{Product(2, 2, 'clam'): 1}] * 2
        self.hammer = Product(2, 2, 'hammer')
        self.big_demand = [{self.hammer: 1}] * 3
        self.complicated_demand = [{Product(1, 1, 'apple'): 1, Product(2, 2, 'clam'): 1}] * 2

    def test_single_no_change(self):
        assert_equal(self.apple_demand, join_demands([self.apple_demand]))

    def test_empty(self):
        assert_equal([], join_demands([]))

    def test_two_values(self):
        result = join_demands([self.apple_demand, self.clam_demand])
        assert_equal(self.complicated_demand, result)

    def test_jagged(self):
        expected = self.complicated_demand
        for item in expected:
            item[self.hammer] = 1
        expected.append(({self.hammer: 1}))
        assert_equal(expected, join_demands([self.apple_demand, self.clam_demand, self.big_demand]))


class TestScaleDemand(unittest.TestCase):
    def setUp(self) -> None:
        self.apple_demand = [{Product(1, 1, 'apple'): 1}] * 10
        self.all_scaled = [{Product(1, 1, 'apple'): 5}] * 10
        self.first_scaled = [{Product(1, 1, 'apple'): 5}]
        self.first_scaled.extend([{Product(1, 1, 'apple'): 1}] * 9)
        self.last_scaled = [{Product(1, 1, 'apple'): 1}] * 9
        self.last_scaled.append({Product(1, 1, 'apple'): 5})

    def test_no_scale(self):
        assert_equal(self.apple_demand, scale_demand(self.apple_demand, 0, 10, 1))

    def test_simple(self):
        assert_equal(self.all_scaled, scale_demand(self.apple_demand, 0, 10, 5))

    def test_first(self):
        assert_equal(self.first_scaled, scale_demand(self.apple_demand, 0, 1, 5))

    def test_last(self):
        assert_equal(self.last_scaled, scale_demand(self.apple_demand, 9, 10, 5))


class TestSimpleDemand(unittest.TestCase):
    def setUp(self) -> None:
        self.apple = Product(1, 1, 'apple')
        self.apple_demand = [{Product(1, 1, 'apple'): 1}]

    def test_no_days(self):
        assert_equal([], generate_simple_demand(self.apple, 0, 100))

    def test_one_or_more(self):
        for i in range(5):
            assert_equal(self.apple_demand * (i + 1), generate_simple_demand(self.apple, i + 1, 1))


class TestDemandToJSON(unittest.TestCase):
    def setUp(self) -> None:
        self.apple_demand = [{Product(1, 1, 'apple'): 1}] * 2

    def test_simple(self):
        assert_equal([
            [
                {
                    "name": "apple",
                    "quantity": 1
                }
            ],
            [
                {
                    "name": "apple",
                    "quantity": 1
                }
            ]
        ], demand_to_json(self.apple_demand))


class TestBuildWorld(unittest.TestCase):
    def test_default(self):
        assert_is_not_none(build_world(generate_world()))
