from model.warehouse import Warehouse


class World:
    """
    Wrapper class to hold all of the data objects in a simulation
    """
    def __init__(self, trucks: set, stores: set, warehouse: Warehouse):
        """
        Sets up the world based on the parsed input
        @param trucks: the list of trucks that are present
        @param stores: the list of stores that are present
        @param warehouse: the warehouse that will be used in the simulation
        """
        self.trucks = {}
        for truck in trucks:
            self.trucks[str(truck)] = truck
        self.stores = {}
        self.products = {}
        for store in stores:
            for product, _ in store.current_products:
                self.products[str(product)] = product
            for day in store.demand:
                for product in day.keys():
                    self.products[str(product)] = product
            self.stores[str(store)] = store
        self.warehouse = warehouse
