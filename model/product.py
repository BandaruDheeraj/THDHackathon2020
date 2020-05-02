class Product:
    """
    Object that will represent a single product sold by a store
    """

    def __init__(self, value: float, weight: float, name: str) -> None:
        """
        Creates a product object
        @param value: The value of the product (could be thought of as revenue or margin, doesn't really matter which)
        @param weight: The weight of the product (can be thought of as a function of volume and weight really)
        @param name: A string name given to the product
        """
        self.value = value
        self.weight = weight
        self.name = name

    def __eq__(self, other):
        result = False
        if isinstance(other, Product):
            result = self.name == other.name and self.value == other.value and self.weight == other.weight
        return result

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.name
