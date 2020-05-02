# THD Hackathon 2020
## Problem Description
- Suppose you are running a store chain and have been given the task of distributing products from your warehouse to the stores you're in charge of
- For each store, you are given a projection of demand for the whole year and need to do your best to meet that demand
- All products come from the warehouse and the inventory at the warehouse is infinite
- The distances from the warehouse to each store as well as the distances between stores are known
    - The distance used in this world is manhattan distance
    - There is no concept of non-integer distances to keep things simple
- Your transportation crew has a fixed number of vehicles and each vehicle is only allowed to travel a maximum distance each day
  - At the beginning of the next day, the range of the vehicle is reset to the full value
  - Vehicles can be left at any point in the map at the end of a day
- The vehicles and stores have a fixed capacity
  - For simplicity, assume this is some combination of volume and weight
  - No store or truck can ever contain more than its capacity worth of products 
- Every day, a truck travel between the stores and the warehouse
  - It can only load inventory from the warehouse
  - It can only offload at a store
  - You can not shuffle products between stores or trucks
- Trucks can arrive at the same store at the same time and they may cross the same road going to different stores
- If a store doesn't have enough inventory for a given product, you can only sell whatever quantity is on hand
- Your job is to route the trucks to distribute the products as optimally as possible across the stores so they can each meet their product demands
- You may stock up certain products to anticipate future sales, however, those products will take up capacity until their are sold 
## Data Contracts
### World Format
The world will be provided as a JSON file in the following format:
```
{
  "trucks": <trucks>,
  "stores": <stores>,
  "warehouse": <warehouse>
  "products": <products>
}
```
#### Truck Format
The trucks available will be provided as a JSON array of objects in the following format:
```
{
    "id": int,
    "x": int,
    "y": int,
    "capacity": float,
    "range": int
}
```
Where:
- `id` is a unique identifier for the truck
- `x` is the initial x coordinate of the truck
- `y` is the initial y coordinate of the truck
- `capacity` is the maximum capacity of products for this truck
- `range` is the movement range for this truck

All trucks will start out carrying 0 products.

#### Warehouse
The warehouse sits at a fixed location and only has x and y coordinates.  For simplicity, assume the inventory at the 
warehouse is infinite.  Trucks can only pick up products when they are at the same location as the warehouse, otherwise
the action will be ignored.
Sample warehouse object:
```
{
    "x": 0,
    "y": 0
}
``` 
#### Products Format
The products array will list all of the different products that are available for the simulation.  In the stores array,
each product will be referred to by its name, which will be a unique identifier.  Each product has a "weight", simply
the metric we'll use for size and a "value", which is the revenue you will receive for selling 1 unit of that product.  

Sample product object:
```
{
    "name": "apple",
    "value": 1,
    "weight": 1
}
```
#### Store Format
The stores array will contain the following information:
```
{
    "id": 0,
    "x": 1,
    "y": 1,
    "capacity": 1,
    "products": <products>,
    "demand": <demand>
}
```
Similar to what we saw for a truck:
- `id` is a unique identifier for the store
- `x` is the initial x coordinate of the store
- `y` is the initial y coordinate of the store
- `capacity` is the maximum capacity of products for this store
We have two new arrays for the store, `products` and `demand`.  
##### Products
`products` is the list of initial products in the store, formatted like:
```
{
    "name": "apple",
    "quantity": 1
}
```
Where:
- `name` matches one of the products in the top-level `products` array
- `quantity` is the quantity of that product that is currently in the store
##### Demand
`demand` is arguably the most important part of the input data.  This array describes what products will be purchased
for each day for the given store.  Each index of the array will be an array of products, and each day, customers will
come to your store and purchase those products, if they are available in the store.  Each product will be formatted the 
same way we saw earlier, namely:
```
{
    "name": "apple",
    "quantity": 1
}
```
Where:
- `name` matches one of the products in the top-level `products` array
- `quantity` is the quantity of that product that is currently in the store
#### Full Sample File
```
{
  "trucks": [
    {
      "id": 0,
      "x": 0,
      "y": 0,
      "capacity": 1,
      "range": 1
    }
  ],
  "stores": [
    {
      "id": 0,
      "x": 1,
      "y": 1,
      "capacity": 1,
      "products": [
        {
          "name": "apple",
          "quantity": 1
        }
      ],
      "demand": [
        [
          {
            "name": "apple",
            "quantity": 1
          }
        ],
        [
          {
            "name": "apple",
            "quantity": 1
          }
        ]
      ]
    }
  ],
  "warehouse": {
    "x": 0,
    "y": 0
  },
  "products": [
    {
      "name": "apple",
      "value": 1,
      "weight": 1
    }
  ]
}
```
### Instructions Format
The instructions accepted is a JSON array where each element is everything you are doing in that day,
 in the following format:
```
[
    <turns>
]
```
Where `<turns>` is a JSON array of ordered moves for that day.  Each move will be executed in the order it is
found in the array.  See the following format:
```
[
    <action>
]
```  
Where `<action>` is one of the following:
#### Movement
```
{
    "action": "move",
    "truck": <id of truck from input data>,
    "x": <new x value>,
    "y": <new y value>
}
```
This action can be performed for any truck at any point in the simulation, provided the truck has enough
range to reach its destination.
#### Loading Product(s) onto a truck
```
{
    "action": "load",
    "truck": <id of truck from input data>,
    "products": [
        {
            "name": <product name from input data>,
            "quantity": <integer>
        }, ...
    ]
}
```
Loading a product with a name not found in the `products` array in the input data will result in an error.
Products will be loaded in the order they are found in the array.  If, at any point, the truck does not have enough
capacity for the remaining products, it will simply not load the rest and continue on.

NOTE:  this action can only be performed when the truck is at the same location as the warehouse.  
If it is not in the same location, the action will be ignored.
#### Unloading products from a truck to a store
```
{
    "action": "unload",
    "truck": <id of truck from input data>,
    "store": <id of store from input data>,
    "products": [
        {
            "name": <product name from input data>,
            "quantity": <integer>
        }, ...
    ]
}
```
Loading a product with a name not found in the `products` array in the input data will result in an error.
Products will be loaded in the order they are found in the array.  If, at any point, the store does not have enough
capacity for the remaining products, it will simply not load the rest and continue on.  If a given product was not
found on the truck, the product will be ignored.

NOTE:  this action can only be performed when the truck is at the same location as the store.  
If it is not in the same location, the action will be ignored.
 
Any value put in the `action` field that is not listed above will result in an error.
#### Sample Input (for the world shown above):
```
[
  [
    {
      "action": "load",
      "truck": 0,
      "products": [
        {
          "name": "apple",
          "quantity": 1
        }
      ]
    },
    {
      "action": "move",
      "truck": 0,
      "x": 1,
      "y": 0
    }
  ],
  [
    {
      "action": "move",
      "truck": 0,
      "x": 1,
      "y": 1
    },
    {
      "action": "unload",
      "truck": 0,
      "store": 0,
      "products": [
        {
          "name": "apple",
          "quantity": 1
        }
      ]
    }
  ]
]
```
## Important Considerations
- For simplicity, distance is Manhattan Distance, see https://en.wikipedia.org/wiki/Taxicab_geometry
- If a truck has 1 or more moves and it runs out of range,
it will not make the final move that would cause it to have a remaining range of < 0
- If you are trying to load more weight than there is room for to a store or truck, there will not be an error,
the simulation will simply ignore everything after the maximum capacity
- Extra JSON keys anywhere in the instruction file will be ignored
- When loading products into a store from a truck, each product will be tried individually in the order provided,
if there is an error, the product will be ignored and the next will be tried
