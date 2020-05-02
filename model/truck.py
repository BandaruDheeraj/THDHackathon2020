from model.storage_entity import StorageEntity
from model.warehouse import Warehouse
from third_module import day, list_truck, list_products, list_store, list_warehouse


RETURN_TO_WAREHOUSE_CAP = 10

class Truck(StorageEntity):

    """
    Class to hold the information about one truck living in the simulation
    Basically, this is a store that can move and has 0 demand
    """

    def __init__(self, max_capacity: float, x: int, y: int, movement_range: int, id: int) -> None:
        """
        @param max_capacity:  The max total weight the store can hold at one time
        @param x: the x location of the store
        @param y: the y location of the store
        @param movement_range: the range of the truck
        @param id: the unique ID of this object
        """
        super().__init__(max_capacity, x, y, [], id)
        self.range = movement_range
        self.moves_left = movement_range
        self.adj_list = []

    def unload(self, store: StorageEntity, products: list) -> None:
        """
        Unloads the specified products into the store and removes them from this truck
        This requires the location of the store and the truck to be the same
        :raises KeyError: if the products specified are not on the truck
        :raises ValueError: if the store cannot hold the products specified
        :raises LocationError: if the truck is not in the same place as the store
        TODO do we want to prevent unloading to another truck?
        """
        if self.x == store.x and self.y == store.y:
            store.add_products(products)
            self.remove_products(products)  # call remove after because it will change the quantity
        else:
            raise LocationError(
                'Truck is not in the same location as the store: truck: {} {}, store: {} {}'.format(self.x, self.y,
                                                                                                    store.x, store.y))

    def get_products(self, warehouse: Warehouse, products: list) -> None:
        """
        Gets products from the warehouse and puts them on the truck
        Requires the truck to be in the same location as the warehouse

        @param warehouse: the warehouse to get products from (there could be more than one in the simulation
        @param products: the products to add to the truck
        :raises ValueError if you try to add more weight than the truck has capacity
        :raises LocationError if the truck and the warehouse are not in the same position
        """
        if self.x == warehouse.x and self.y == warehouse.y:
            self.current_products = products
        else:
            raise LocationError('Truck is not in the same location as the warehouse: truck: {} {}, warehouse: {} {}'.format(self.x, self.y, warehouse.x, warehouse.y))

    def calc_reward(self, dist, store):

        demand_list = store.demand
        demand_day_list = demand_list[day]
        product_demand = []
        product_list = []
        davo = 0
        for i in demand_day_list:
            product_demand.append((i['name'], i['quantity']))
        for i, quantity in self.current_products:
            for j in range(0 , len(product_demand)):
                if i.name == product_demand[j][0]:
                    if product_demand[j][1] >= quantity:
                        #for mosey in range(0, product_demand[j][1]):
                        product_list.append((i, quantity))
                        davo += (i.value * product_demand[j][1])
                    else:
                        #for mosey in range(0, self.count(i.name)):
                        product_list.append((i, product_demand[j][1] - 1))
                        davo += (i.value * quantity)
        reward = davo/dist

        
        return reward, product_list

    def reward_function(self):
        adj_list = []
        if self.x == list_warehouse[0].x and self.y == list_warehouse[0].y:
            adj_list = list_warehouse[0].adj_list
        else:
            adj_list = self.make_adj_lists_from_truck()
        reward_list = []
        max_id = None 
        max_reward = float('-inf')
        max_dist = 0
        for id, dist in adj_list:
            reward, product_list = self.calc_reward(dist, list_store[id])
            print(reward)
            if reward > max_reward:
                max_reward = reward
                max_id = id
                reward_list = product_list
                max_dist = dist
        return max_id, reward_list, max_reward, max_dist

    def count(self, name):
        count = 0
        for i, quantity in self.current_products:
            if i.name == name:
                count += 1
        return count

    def can_move(self):
        if(self.moves_left > 0):
            return True
        return False
    
    def move(self, new_x, new_y):
        """
        Simple movement of the truck.  Attempts to move from self.x, self.y to new_x, new_y.  Distance used will be
        manhattan distance
        @param new_x: the new x coordinate
        @param new_y: the new y coordinate
        :raises MovementError if the truck cannot make it to its destination
        """
        distance = abs(self.x - new_x) + abs(self.y - new_y)
        self.moves_left -= distance
        if self.moves_left >= 0:
            self.x = new_x
            self.y = new_y
        else:
            raise MovementError('{} moved {} units too far'.format(str(self), self.moves_left * -1))

    def end_turn(self):
        """
        resets the number of moves for the next turn
        """
        self.moves_left = self.range

    def __eq__(self, other):
        equal = False
        if isinstance(other, Truck):
            equal = super().__eq__(other) and self.range == other.range and self.moves_left == other.moves_left
        return equal

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return 'truck_{}'.format(self.id)
    
    def make_adj_lists_from_truck(self):
        x_pos = 0
        y_pos = 0
        j = 0
        store_list = list_store

        for davo in store_list:
            list_warehouse[0].adj_list.append((davo.id, abs(davo.x) + abs(davo.y)))
        x_pos = self.x
        y_pos = self.y
        while(j < len(store_list)):
            x2_pos = store_list[j].x
            y2_pos = store_list[j].y
            total_distance = abs(x2_pos - x_pos) + abs(y2_pos - y_pos)
            if(total_distance > self.moves_left):
                total_distance = float('inf')
            self.adj_list.append((self.id, total_distance))
        j = j + 1
        self.adj_list.append(('warehouse', abs(x_pos)+ abs(y_pos)))
        return self.adj_list



class LocationError(ValueError):
    """
    Error to specify that the truck is not in the same place as a store or warehouse
    """


class MovementError(ValueError):
    """
    Error to specify that the truck has run out of moves
    """
