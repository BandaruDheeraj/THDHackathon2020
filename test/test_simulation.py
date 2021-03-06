import json
import os
import unittest

from nose.tools import assert_equal, raises

from controller.simulation import build_world, validate_and_parse_instructions, run_simulation
from model.product import Product
from model.store import Store
from model.truck import Truck

TEST_FILE_PATH = 'test/input_files'

TWO_TURN_INPUT = [
    [
        {
            "action": "load",
            "truck": 'truck_0',
            "products": [
                {
                    "name": "apple",
                    "quantity": 1
                }
            ]
        },
        {
            "action": "move",
            "truck": 'truck_0',
            "x": 1,
            "y": 0
        }
    ],
    [
        {
            "action": "move",
            "truck": 'truck_0',
            "x": 1,
            "y": 1
        },
        {
            "action": "unload",
            "truck": 'truck_0',
            "store": 'store_0',
            "products": [
                {
                    "name": "apple",
                    "quantity": 1
                }
            ]
        }
    ]
]


# note that world validation will be done in the data_generator tests, this is just loading data, assuming it was
# generated by our code
class TestBuildWorld(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(TEST_FILE_PATH, 'world', 'empty_world.json')) as fin:
            data = fin.read().encode('utf-8')
        self.empty_world = json.loads(data)
        with open(os.path.join(TEST_FILE_PATH, 'world', 'simple_world.json')) as fin:
            data = fin.read().encode('utf-8')
        self.simple_world = json.loads(data)
        with open(os.path.join(TEST_FILE_PATH, 'world', 'full_world.json')) as fin:
            data = fin.read().encode('utf-8')
        self.full_world = json.loads(data)

    def test_load_empty_world(self):
        world = build_world(self.empty_world)
        assert_equal({}, world.trucks)
        assert_equal({}, world.stores)
        assert_equal({}, world.products)
        assert_equal(0, world.warehouse.x)
        assert_equal(0, world.warehouse.y)

    def test_load_simple_world(self):
        world = build_world(self.simple_world)
        assert_equal({'truck_0': Truck(0, 0, 0, 0, 0)}, world.trucks)
        assert_equal({'store_0': Store(0, 1, 1, [], [], 0)}, world.stores)
        assert_equal({}, world.products)
        assert_equal(0, world.warehouse.x)
        assert_equal(0, world.warehouse.y)

    def test_load_full_world(self):
        world = build_world(self.full_world)
        apple = Product(1, 1, "apple")
        assert_equal({'truck_0': Truck(1, 0, 0, 1, 0)}, world.trucks)
        assert_equal({'store_0': Store(1., 1, 1, [(apple, 1)], [{apple: 1}, {apple: 1}], 0)}, world.stores)
        assert_equal({'apple': apple}, world.products)
        assert_equal(0, world.warehouse.x)
        assert_equal(0, world.warehouse.y)

    @raises(KeyError)
    def test_empty(self):
        build_world({})

    @raises(KeyError)
    def test_no_warehouse(self):
        build_world({'trucks': [], 'products': [], 'stores': []})

    @raises(KeyError)
    def test_no_stores(self):
        build_world({'trucks': [], 'products': [], 'warehouse': {}})

    @raises(KeyError)
    def test_no_trucks(self):
        build_world({'warehouse': {}, 'products': [], 'stores': []})

    @raises(KeyError)
    def test_no_products(self):
        build_world({'trucks': [], 'stores': [], 'warehouse': {}})

    @raises(KeyError)
    def test_product_in_store_but_not_product_list(self):
        self.full_world['products'] = []
        build_world(self.full_world)


class TestValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.bad_path = 'not a path yo'
        self.empty_valid = os.path.join(TEST_FILE_PATH, 'instructions', 'empty.json')
        self.valid = os.path.join(TEST_FILE_PATH, 'instructions', 'valid.json')
        self.bad_truck = os.path.join(TEST_FILE_PATH, 'instructions', 'bad_truck.json')
        self.bad_store = os.path.join(TEST_FILE_PATH, 'instructions', 'bad_store.json')
        self.bad_product = os.path.join(TEST_FILE_PATH, 'instructions', 'bad_product.json')
        self.invalid_action = os.path.join(TEST_FILE_PATH, 'instructions', 'invalid_action.json')
        self.not_json = os.path.join(TEST_FILE_PATH, 'instructions', 'not_json.json')
        with open(os.path.join(TEST_FILE_PATH, 'world', 'full_world.json'), 'rb') as fin:
            data = fin.read().decode('utf-8')
        self.world = build_world(json.loads(data))

    @raises(FileNotFoundError)
    def test_bad_path(self):
        validate_and_parse_instructions(self.bad_path, self.world)

    @raises(KeyError)
    def test_bad_store(self):
        validate_and_parse_instructions(self.bad_store, self.world)

    @raises(KeyError)
    def test_bad_product(self):
        validate_and_parse_instructions(self.bad_product, self.world)

    @raises(KeyError)
    def test_bad_truck(self):
        validate_and_parse_instructions(self.bad_truck, self.world)

    @raises(ValueError)
    def test_invalid_action(self):
        validate_and_parse_instructions(self.invalid_action, self.world)

    def test_empty(self):
        assert_equal([], validate_and_parse_instructions(self.empty_valid, self.world))

    def test_valid(self):
        assert_equal(TWO_TURN_INPUT, validate_and_parse_instructions(self.valid, self.world))


class TestRunSimulation(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(TEST_FILE_PATH, 'world', 'full_world.json'), 'rb') as fin:
            data = fin.read().decode('utf-8')
        self.world = build_world(json.loads(data))

    def test_empty(self):
        assert_equal(0., run_simulation([], self.world))

    def test_one_turn_and_moves_reset(self):
        assert_equal(1., run_simulation([TWO_TURN_INPUT[0]], self.world))
        assert_equal(1, self.world.trucks['truck_0'].x)
        assert_equal(0, self.world.trucks['truck_0'].y)
        assert_equal(1, self.world.trucks['truck_0'].moves_left)

    def test_product_delivered(self):
        assert_equal(2., run_simulation(TWO_TURN_INPUT, self.world))
        assert_equal(1, self.world.trucks['truck_0'].x)
        assert_equal(1, self.world.trucks['truck_0'].y)
