db = DB()
table = db.create_table("test")
table.create_index(
    Index('id', unique=True, auto_increment=True)
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

table.append(
    {'data': [0, 0, 3]}
)


f1 = Filter().data[2] == 3
f2 = Filter().id < 2

print(list(f1(table)))
print(list(f2(table)))
print(list((f1 | f2)(table)))
