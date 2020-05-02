from model.storage_entity import StorageEntity


class Store(StorageEntity):
    """
    Class to hold information about a store, which will also remove products according to demand each turn
    """

    def __init__(self, max_capacity: float, x: int, y: int, starting_products: list, demand: list, id: int) -> None:
        """
        @param max_capacity:  The max total weight the store can hold at one time
        @param x: the x location of the store
        @param y: the y location of the store
        @param starting_products: A list of product object to quantity pairs that the store should start with
                NOTE:  this will be validated to ensure the starting products does not exceed max_capacity
        @param demand: a list of  product to a list of quantities that customers want to buy per day
        @param id: the unique ID of this object
        """
        super().__init__(max_capacity, x, y, starting_products, id)
        self.demand = demand
        self.adj_list = []

    def do_turn(self, current_turn) -> float:
        """
        Decreases the quantity of all the products in the store by the demand, and returns the total revenue earned
        @param current_turn The index of the current turn, so we know which demand value to use
        @return the total revenue from the day of sales
        TODO update demand
        """
        demand = self.demand[current_turn]
        keys = demand.keys()
        to_remove = []
        total_value = 0
        for product, quantity in self.current_products:
            if product in keys:
                remove_count = min(quantity, demand[product])
                total_value += product.value * remove_count
                to_remove.append((product, remove_count))
        # todo handle missing inventory
        self.remove_products(to_remove)
        return total_value
        

    def __eq__(self, other):
        equal = False
        if isinstance(other, Store):
            equal = super().__eq__(other) and self.demand == other.demand
        return equal

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return 'store_{}'.format(self.id)

