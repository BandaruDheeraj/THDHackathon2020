import json
import os

from model.product import Product
from model.store import Store
from model.truck import Truck, MovementError
from model.warehouse import Warehouse
from model.world import World

VALID_MOVES = {'move', 'unload', 'load'}


def run_simulation(instructions: list, world: World) -> float:
    """
    Runs the simulation with the provided instructions
    Note that when a store runs out of demand, it will simply stop selling products
    @param instructions the list of moves for each turn
    @param world the world to run the instructions in
    @return the total revenue generated with the instructions
    """
    revenue = 0.
    for day in range(len(instructions)):
        current_day = instructions[day]
        for move in current_day:
            truck = world.trucks[move['truck']]
            if move['action'] == 'move':
                try:
                    truck.move(move['x'], move['y'])
                except MovementError as e:
                    print('WARNING: MovementError on Day {}, {}'.format(day, e))
            elif move['action'] == 'load':
                if truck.x == world.warehouse.x and truck.y == world.warehouse.y:
                    for product in move['products']:
                        old_products = truck.current_products
                        try:
                            truck.add_products([(world.products[product['name']], product['quantity'])])
                        except ValueError:
                            print('WARNING: tried to add too much to truck {} on Day {}'.format(truck.id, day))
                            truck.set_products(old_products)
                            break  # no sense in trying to continue adding things
                else:
                    print('WARNING: tried to load truck at day {} but truck was not at warehouse, real location: {}, {}'
                          .format(day, truck.x, truck.y))
            elif move['action'] == 'unload':
                store = world.stores[move['store']]
                if truck.x == store.x and truck.y == store.y:
                    truck_products = truck.current_products
                    store_products = store.current_products
                    for product in move['products']:
                        to_remove = (world.products[product['name']], product['quantity'])
                        try:
                            truck.remove_products([to_remove])
                            store.add_products([to_remove])
                        except ValueError:
                            print('WARNING: tried to unload product from truck to store at day '
                                  '{} but encountered an error'.format(day))
                            store.set_products(store_products)
                            truck.set_products(truck_products)
                else:
                    print('WARNING: tried to unload truck at day {} but truck was not at store, real location: {}, {}'
                          .format(day, truck.x, truck.y))
        for truck in world.trucks.values():
            truck.end_turn()
        for store in world.stores.values():
            revenue += store.do_turn(day)
    return revenue


def validate_and_parse_instructions(file_path: str, world: World) -> list:
    """
    Attempts to read the file and convert it into a set of instructions
    @param file_path The path to the instructions file to be read
    @param world The world to execute the instructions in
    @raises ValueError if there were any logic errors
    @raises KeyError if any required fields were missing
    @raises FileNotFoundError if the file does not exist
    @raises JSONDecodeError if the file is not valid JSON
    """
    with open(file_path, 'rb') as fin:
        data = fin.read().decode('utf-8')
    parsed = json.loads(data)
    turns = []
    for turn in parsed:
        moves = []
        for move in turn:
            action = move['action']
            if action in VALID_MOVES:
                truck = str(world.trucks['truck_{}'.format(move['truck'])])  # this requires the key to exist
                # note that since we know how the hash for trucks/stores are constructed, we don't need to create an
                # object in order to look it up in a set
                if action == 'move':
                    moves.append({
                        'action': action,
                        'truck': truck,
                        'x': move['x'],
                        'y': move['y']
                    })
                else:
                    # unload is the same as load with one extra key
                    products = []
                    for product in move['products']:
                        prod = str(world.products[product['name']])
                        products.append({
                            'name': prod,
                            'quantity': int(product['quantity'])
                        })
                    value = {
                        'action': action,
                        'truck': truck,
                        'products': products
                    }
                    if action == 'unload':
                        value['store'] = str(world.stores['store_{}'.format(move['store'])])
                    moves.append(value)
            else:
                raise ValueError('invalid action: action: {}'.format(action))
        turns.append(moves)
    return turns


def build_world(parsed_input: dict) -> World:
    """
    Builds a World object from the input dictionary
    @param parsed_input: the parsed JSON from an input file
    @raises KeyError: if something is missing
    """
    warehouse = Warehouse(parsed_input['warehouse']['x'], parsed_input['warehouse']['y'])
    truck_list = parsed_input['trucks']
    trucks = []
    for truck in truck_list:
        trucks.append(Truck(truck['capacity'], truck['x'], truck['y'], truck['range'], truck['id']))
    product_list = parsed_input['products']
    product_map = {}
    for product in product_list:
        name = product['name']
        product_map[name] = Product(product['value'], product['weight'], name)
    store_list = parsed_input['stores']
    stores = []
    for store in store_list:
        demand_list = []
        for day in store['demand']:
            demand_map = {}
            for demand in day:
                product = product_map[demand['name']]  # will throw an error if it wasn't initialized
                demand_map[product] = demand['quantity']
            demand_list.append(demand_map)
        store_products = []
        for initial in store['products']:
            product = product_map[initial['name']]  # will throw an error if it wasn't initialized
            element = (product, int(initial['quantity']))
            store_products.append(element)
        stores.append(Store(float(store['capacity']), store['x'], store['y'], store_products, demand_list, store['id']))
    return World(set(trucks), set(stores), warehouse)


# sample of how to test you input file
if __name__ == '__main__':
    # NOTE:  run this file with the working directory set to the project root, not controller
    with open(os.path.join('worlds', 'final_world.json'), 'rb') as fin:
        # modify this path to the world that you want to load
        data = fin.read().decode('utf-8')
    parsed_world = build_world(json.loads(data))
    # modify this path to the instructions file that you want to use
    parsed_instructions = validate_and_parse_instructions(
        os.path.join('test', 'input_files', 'instructions', 'valid.json'), parsed_world)
    print('Revenue earned: ${}'.format(run_simulation(parsed_instructions, parsed_world)))

#export PYTHONPATH=/home/dheeraj/Projects/THDHackathon2020/
