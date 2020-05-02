import json
import parse_json
from third_module import *
import random

def main():
    parse_json.parse_json("first_world.json")
    parse_json.random_load()
    parse_json.make_adj_lists()
    
    RETURN_TO_WAREHOUSE_CAP = 10
    stores = parse_json.get_store_list()
    max_days = len(stores[0].demand)
    i = 0

    while(i < max_days):
        for davo in list_truck:
            while(davo.moves_left > 1):
                if len(davo.current_products) < RETURN_TO_WAREHOUSE_CAP:
                    if (abs(davo.x) + abs(davo.y) <= davo.moves_left):
                        davo.move(list_warehouse[0].x, list_warehouse[0].y)
                        product_list = []
                        max_cap = davo.max_capacity
                        count = 0
                        while(count < max_cap):
                            val = random.randint(0, len(list_products) - 1)
                            product = list_products[val]
                            count += product.weight
                            hah = random.randint(0, int(max_cap/ product.weight))
                            if (count * hah < max_cap):
                                product_list.append((product, hah))
                            davo.get_products(list_warehouse[0], product_list)
                    else:
                        davo.move(davo.x - (abs(davo.x) + abs(davo.y))/2, davo.y - (abs(davo.x) + abs(davo.y)/2))
                id, tory, reward, dist = davo.reward_function()
                # store = list_store[id]
                # new_x = store.x
                # new_y = store.y
                if dist > davo.moves_left:
                    davo.move(davo.x - davo.moves_left/2, davo.y - davo.moves_left/2)
                else:
                    davo.move(stores[id].x, stores[id].y)
                    for index in range(0, len(tory)):
                        for ind in range(0, len(product_list)):
                            if tory[index][0] == product_list[ind][0]:
                                if(tory[index][1] > product_list[ind][1]): 
                                    tory[ind] = list(tory[ind])
                                    tory[ind][1] = product_list[index][1]
                                    tory[ind] = tuple(tory[ind])
                    davo.unload(stores[id], tory)
    import third_module
    third_module.day = third_module.day + 1

                
                
def check_if_at_store(predict_x, predict_y):
    for store in list_store:
        if(store.x == predict_x and store.y == predict_y):
            return True
        return False

def new_day(self):
    for x in list_truck:
        x.reward_function()
    self.day += 1
	

main()
            