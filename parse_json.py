import json
import random
from model.truck import Truck
from model.store import Store
from model.warehouse import Warehouse
from model.product import Product
from third_module import day, list_truck, list_products, list_store, list_warehouse
DAYS_IN_ADVANCE = 2
EXTRA_DISTANCE_THRESH = 0.1
RETURN_TO_WAREHOUSE_CAP = 10


def parse_json(input_file):
	with open('worlds/' + input_file) as input_data:
		data = json.load(input_data)
		
	init_list_truck = data['trucks']
	init_list_store = data['stores']
	init_list_warehouse = data['warehouse']
	init_list_products = data['products']

	for x in init_list_truck:
		list_truck.append(Truck(x['capacity'], x['x'], x['y'], x['range'],x['id']))

	for x in init_list_store:
		list_store.append(Store(x['capacity'], x['x'], x['y'], x['products'],x['demand'], x['id']))
	
	list_warehouse.append(Warehouse(init_list_warehouse['x'], init_list_warehouse['y']))

	for x in init_list_products:
		list_products.append(Product(x['value'],x['weight'],x['name']))

def get_truck_list():
	return list_truck

def get_store_list():
	return list_store

def get_warehouse_list():
	return list_warehouse

def get_products_list():
	return list_products


def random_load():
	max_cap = 0
	products = get_products_list()
	for y in get_truck_list():
		product_list = []
		max_cap = y.max_capacity
		count = 0
		while(count < max_cap):
			val = random.randint(0, len(get_products_list()) - 1)
			product = products[val]
			count += product.weight
			hah = random.randint(0, int(max_cap/ product.weight))
			if (count * hah < max_cap):
				product_list.append((product, hah))
			count = count * hah
		y.get_products(list_warehouse[0], product_list)

	
def make_adj_lists():
	x_pos = 0
	y_pos = 0
	i = 0
	j = 1
	store_list = get_store_list()

	for davo in store_list:
		list_warehouse[0].adj_list.append((davo.id, abs(davo.x) + abs(davo.y)))
	while(i < len(store_list)):
		x_pos = store_list[i].x
		y_pos = store_list[i].y
		while(j < len(store_list)):
			if(j != i):
				x2_pos = store_list[j].x
				y2_pos = store_list[j].y
				total_distace = abs(x2_pos - x_pos) + abs(y2_pos - y_pos)
				store_list[i].adj_list.append((store_list[j].id, total_distace)) # distance between store_list[i] and store_list[j]
			j = j + 1
		j = 0
		store_list[i].adj_list.append(('warehouse', abs(x_pos) + abs(y_pos)))
		i = i + 1


parse_json('final_world.json')
random_load()
make_adj_lists()
