import unittest

from nose.tools import assert_equal, raises

from model.product import Product
from model.storage_entity import StorageEntity
from model.store import Store
from model.truck import Truck, LocationError, MovementError
from model.warehouse import Warehouse


class TestStorageEntity(unittest.TestCase):
    def setUp(self) -> None:
        self.single_product_map = [
            (Product(1, 1, 'apple'), 20)
        ]
        self.two_product_map = [
            (Product(1, 1, 'apple'), 20),
            (Product(1, 2, 'clam'), 5)
        ]

    # constructor tests
    def test_validation_single_product_is_valid(self):
        store = StorageEntity(20, 1, 1, self.single_product_map, 0)
        assert_equal(self.single_product_map, store.current_products)
        assert_equal(20., store.current_weight)

    @raises(ValueError)
    def test_validation_single_product_too_heavy(self):
        StorageEntity(19, 1, 1, self.single_product_map, 0)

    def test_validation_double_product_is_valid(self):
        store = StorageEntity(30, 1, 1, self.two_product_map, 0)
        assert_equal(self.two_product_map, store.current_products)
        assert_equal(30., store.current_weight)

    @raises(ValueError)
    def test_validation_double_product_too_heavy(self):
        StorageEntity(29, 1, 1, self.two_product_map, 0)

    def test_no_products(self):
        store = StorageEntity(1, 1, 1, [], 0)
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

        store = StorageEntity(1, 1, 1, None, 0)
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

    # add product tests
    @raises(ValueError)
    def test_add_product_invalid(self):
        store = StorageEntity(30, 1, 1, self.two_product_map, 0)
        store.add_products([(Product(1, 1, ''), 1)])

    def test_add_product_valid(self):
        store = StorageEntity(33, 1, 1, self.two_product_map, 0)
        store.add_products([(Product(1, 1, ''), 1)])
        assert_equal(31, store.current_weight)
        store.add_products([(Product(1, 1, ''), 2)])
        assert_equal(33, store.current_weight)

    # remove product tests
    @raises(KeyError)
    def test_remove_product_not_there_empty_storage(self):
        store = StorageEntity(30, 1, 1, [], 0)
        store.remove_products(self.single_product_map)

    @raises(KeyError)
    def test_remove_product_not_there_non_empty_storage(self):
        store = StorageEntity(30, 1, 1, self.single_product_map, 0)
        store.remove_products([self.two_product_map[1]])

    def test_remove_product_happy_path(self):
        store = StorageEntity(30, 1, 1, self.two_product_map, 0)
        store.remove_products(self.single_product_map)
        assert_equal(10, store.current_weight)
        assert_equal([(Product(1, 2, 'clam'), 5)], store.current_products)

    def test_remove_nothing_does_nothing(self):
        store = StorageEntity(33, 1, 1, self.two_product_map, 0)
        store.remove_products([])
        assert_equal(self.two_product_map, store.current_products)
        assert_equal(30., store.current_weight)

    def test_remove_less_than_all(self):
        store = StorageEntity(30, 1, 1, self.single_product_map, 0)
        store.remove_products([(Product(1, 1, 'apple'), 1)])
        assert_equal(19, store.current_weight)

    @raises(KeyError)
    def test_remove_more_than_all(self):
        store = StorageEntity(30, 1, 1, self.single_product_map, 0)
        store.remove_products([(Product(1, 1, 'apple'), 21)])


class TestTruck(unittest.TestCase):
    def setUp(self) -> None:
        self.single_product_map = [
            (Product(1, 1, 'apple'), 20)
        ]
        self.two_product_map = [
            (Product(1, 1, 'apple'), 20),
            (Product(1, 2, 'clam'), 5)
        ]

    # unload tests
    def test_unload_happy(self):
        store = StorageEntity(30, 1, 1, [self.two_product_map[1]], 0)
        truck = Truck(30, 1, 1, 0, 0)
        truck.add_products(self.single_product_map)
        truck.unload(store, truck.current_products)
        assert_equal([self.two_product_map[1], self.two_product_map[0]], store.current_products)
        assert_equal(30., store.current_weight)

    @raises(LocationError)
    def text_unload_wrong_x(self):
        store = StorageEntity(30, 2, 1, [self.two_product_map[1]], 0)
        truck = Truck(30, 1, 1, 0, 0)
        truck.add_products(self.single_product_map)
        truck.unload(store, truck.current_products)

    @raises(LocationError)
    def text_unload_wrong_y(self):
        store = StorageEntity(30, 1, 2, [self.two_product_map[1]], 0)
        truck = Truck(30, 1, 1, 0, 0)
        truck.add_products(self.single_product_map)
        truck.unload(store, truck.current_products)

    # get_products tests
    @raises(LocationError)
    def test_get_products_wrong_x(self):
        warehouse = Warehouse(2, 1)
        truck = Truck(30, 1, 1, 0, 0)
        truck.get_products(warehouse, self.single_product_map)

    @raises(LocationError)
    def test_get_products_wrong_y(self):
        warehouse = Warehouse(1, 2)
        truck = Truck(30, 1, 1, 0, 0)
        truck.get_products(warehouse, self.single_product_map)

    def test_get_products_happy(self):
        warehouse = Warehouse(1, 1)
        truck = Truck(30, 1, 1, 0, 0)
        truck.get_products(warehouse, self.single_product_map)
        assert_equal(20, truck.current_weight)
        assert_equal(self.single_product_map, truck.current_products)

    # move tests
    @raises(MovementError)
    def test_move_too_far(self):
        truck = Truck(30, 1, 1, 1, 0)
        truck.move(2, 2)

    def test_move_valid(self):
        truck = Truck(30, 1, 1, 1, 0)
        truck.move(2, 1)
        assert_equal(2, truck.x)
        assert_equal(1, truck.y)
        assert_equal(0, truck.moves_left)

    def test_end_turn(self):
        truck = Truck(30, 1, 1, 1, 0)
        truck.move(2, 1)
        truck.end_turn()
        assert_equal(1, truck.moves_left)


class TestStore(unittest.TestCase):
    def setUp(self) -> None:
        self.simple_demand = [{Product(1, 1, 'apple'): 1}] * 2
        self.complicated_demand = [{Product(1, 1, 'apple'): 1, Product(2, 2, 'clam'): 2}] * 2

    def test_end_turn_no_inventory(self):
        store = Store(0, 0, 0, [], self.simple_demand, 0)
        assert_equal(0, store.do_turn(0))
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

    def test_end_turn_with_inventory(self):
        store = Store(1, 0, 0, [(Product(1, 1, 'apple'), 1)], self.simple_demand, 0)
        assert_equal(1, store.do_turn(0))
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

    def test_two_turns_with_inventory(self):
        store = Store(1, 0, 0, [(Product(1, 1, 'apple'), 1)], self.simple_demand, 0)
        assert_equal(1, store.do_turn(0))
        assert_equal(0, store.do_turn(1))
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

    def test_end_turn_with_some_inventory_complicated_demand(self):
        store = Store(1, 0, 0, [(Product(1, 1, 'apple'), 1)], self.complicated_demand, 0)
        assert_equal(1, store.do_turn(0))
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)

    def test_end_turn_with_all_inventory_complicated_demand(self):
        store = Store(10, 0, 0, [(Product(1, 1, 'apple'), 1), (Product(2, 2, 'clam'), 2)], self.complicated_demand, 0)
        assert_equal(5, store.do_turn(0))
        assert_equal(0, store.current_weight)
        assert_equal([], store.current_products)
