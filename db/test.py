from db.core import *

db = DB()
table = db.create_table("test")
table.create_index(
    Index('id', unique=True, not_none=True)
)

table.append(
    {'id': 0, 'data': [[1, 2, 3], 2, 3]}
)

table.append(
    {'id': 1, 'data': [[3, 2, 1], 2, 1]}
)

table.append(
    {'id': 2, 'data': [[3, 2, 1], 2, [5, 6, 7]]}
)


f = Filter().data[2] == 3

result = f(table)

print(result)
print(list(result))
