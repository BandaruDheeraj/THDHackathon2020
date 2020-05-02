from copy import deepcopy


class StorageEntity:
    """
    Object that will represent a store that sells products
    """

    def __init__(self, max_capacity: int, x: int, y: int, starting_products: list, id: int) -> None:
        """
        @param max_capacity:  The max total weight the store can hold at one time
        @param x: the x location of the store
        @param y: the y location of the store
        @param starting_products: A list of product object to quantity pairs that the store should start with
                NOTE:  this will be validated to ensure the starting products does not exceed max_capacity
        @param id: the unique ID of this object
        """
        self.id = id
        self.max_capacity = max_capacity
        self.x = x
        self.y = y
        self.current_weight = 0
        self.current_products = []
        if starting_products is not None and len(starting_products) > 0:
            self.set_products(starting_products)

    def get_current_weight(self) -> int:
        """
        Calculates the total weight of the current set of products
        """
        total_weight = 0
        for product, quantity in self.current_products:
            total_weight += product.weight * quantity
        self.current_weight = total_weight
        return self.current_weight

    def set_products(self, new_products: list) -> None:
        """
        Replaces the entire set of products in the store with new_products
        This will also filter out any instances of products with 0 quantity
        @param new_products: the new set of products to put in the store
        NOTE all previous products will be removed
        @raises ValueError: if the new products weigh too much for the store
        """
        new_products = filter(lambda element: element[1] > 0, new_products)
        self.current_products = list(new_products)
        self.get_current_weight()
        if self.current_weight > self.max_capacity:
            raise ValueError(
                'not enough capacity to hold starting products, weight {}, capacity {}'.format(self.current_weight,
                                                                                               self.max_capacity))
        # unify products
        unified = {}
        for product, quantity in self.current_products:
            if product in unified:
                unified[product] += quantity
            else:
                unified[product] = quantity
        self.current_products = []
        for product, quantity in unified.items():
            self.current_products.append((product, quantity))

    def add_products(self, products: list) -> None:
        """
        Adds the products to the store's inventory if possible
        @param products: list of product, quantity pairs to add to the store
        @raises ValueError if there is not enough capacity to hold all the products
        """
        current_products = deepcopy(self.current_products)
        for value in products:
            current_products.append(value)
        self.set_products(current_products)

    def remove_products(self, products: list) -> None:
        """
        Removes the specified products from the inventory if they are present
        @param products: the products to remove
        @raises KeyError if there were any products in the list that are not in the inventory
        """
        has_error = False
        if len(products) > 0:  # first check if there is anything to remove
            for product, quantity in products:
                removed = False
                for i in range(len(self.current_products)):
                    product_in_stock, on_hand = self.current_products[i]
                    if product == product_in_stock:
                        if on_hand >= quantity:
                            self.current_products[i] = (product, on_hand - quantity)
                            removed = True
                if not removed:
                    has_error = True
                    break
            # handle 0 quantity
            self.set_products(self.current_products)
        if has_error:
            raise KeyError('Trying to either remove a product not present or too much of a product')

    def __eq__(self, other):
        equal = False
        if isinstance(other, StorageEntity):
            equal = self.x == other.x and self.y == other.y and self.current_weight == other.current_weight and\
                    self.current_products == other.current_products and self.id == other.id and\
                    self.max_capacity == other.max_capacity
        return equal

    # note hash will not be implemented here.  Raw StorageEntity classes should not exist in a set together