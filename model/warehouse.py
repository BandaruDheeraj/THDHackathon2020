class Warehouse:
    """
    Really just a simple class to hold the coordinates of the warehouse, we assume the warehouse has infinite
    inventory
    """
    def __init__(self, x: int, y: int) -> None:
        """
        @param x: The x coordinate of the warehouse
        @param y: The y coordinate of the warehouse
        """
        self.x = x
        self.y = y
        self.adj_list = []
