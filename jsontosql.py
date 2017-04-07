#!/usr/bin/env python

import json
import os
import sqlite3
import sys

DDL = ['''

-- Items are identified by their name even (especially ?) across mod boundaries
create table item(
    name varchar(32) UNIQUE
);

''', '''

-- Each recipe in each mod gets their own entry in this table
create table recipe(
    id int PRIMARY KEY,
    name varchar(32),
    mod_pack varchar(32)
);

''', '''

-- Each entry means that one invocation of the referenced recipe requires
-- 'count' instances of the item referenced by 'ingredient'
create table recipe_ingredient(
    recipe int,
    ingredient int,
    count numeric,
    FOREIGN KEY(recipe) references recipe(id),
    FOREIGN KEY(ingredient) references item
);

''', '''

-- Each entry means that one invocation of the referenced recipe creates
-- 'count' instances of the item referenced by 'product'
create table recipe_product(
    recipe int,
    product int,
    count numeric,
    FOREIGN KEY(recipe) references recipe(id),
    FOREIGN KEY(product) references item
);

''']

def usage():
    print "%s: [extracts-directory]" % sys.argv[0]

def guarantee_schema(conn):
    'Create the db-schema (if needed)'
    curs = conn.cursor()

    # Does the item table exist?
    try:
        curs.execute('select count(*) from item;')
        # If the above didn't throw, assume the rest of the schema is intact.
        return
    except sqlite3.DatabaseError:
        pass

    # Need to run our ddl
    for ddl in DDL:
        curs.execute(ddl)

def do_inserts(curs, items, table_name):
    if not items:
        return

    params = ', '.join('?' * len(items[0]))
    for item in items:
        curs.execute('insert into ' + table_name + ' values (' + params + ');', item)

def resolve_item(record, lst):
    copy = list(record)
    val = copy[1]
    idx = lst.index((val,)) + 1 # records in 'item' are 1-indexed by rowid...
    copy[1] = idx
    return tuple(copy)

resolve_ingredient = resolve_item
resolve_product = resolve_item

def process_mod_pack(mod_pack, recipes, techs, accumulators):
    items = accumulators['items']
    recs = accumulators['recs']
    rec_count = accumulators['rec_count']
    ings = accumulators['ings']
    prods = accumulators['prods']

    # For each item, 'add' it to the item_accumulator
    for name, recipe in recipes.iteritems():
        rec_count += 1
        recs.append((rec_count, name, mod_pack))

        for ing in recipe['ingredients']:
            items.add((ing['name'],))
            ings.append((rec_count, ing['name'], ing['amount']))

        for prod in recipe['products']:
            items.add((prod['name'],))

            # Variable outputs are encoded via min_amount/max_amount... let's
            # use the mean because that's good enough for my purposes :p
            amt = prod.get('amount')
            if amt is None:
                amt = (prod['amount_min'] + prod['amount_max']) / 2.0

            prods.append((rec_count, prod['name'], amt))

    accumulators['rec_count'] = rec_count

def read_json(fname):
    return json.load(open(fname, 'rb'))

def main(args):
    if not args:
        args = ["extracts"]

    if len(args) != 1:
        usage()
        sys.exit(1)

    extracts = args[0]
    mod_packs = os.listdir(extracts)

    acc = {
        'items': set(),
        'recs': [],
        'rec_count': 0,
        'ings': [],
        'prods': []
    }

    for mod_pack in mod_packs:
        recipes = read_json(os.path.join(extracts, mod_pack, 'recipes.json'))
        techs = read_json(os.path.join(extracts, mod_pack, 'technologies.json'))

        process_mod_pack(mod_pack, recipes, techs, acc)

    # Need to resolve ingredient and process ids
    items = sorted(acc['items'])
    for i in xrange(len(acc['ings'])):
        acc['ings'][i] = resolve_ingredient(acc['ings'][i], items)
    for i in xrange(len(acc['prods'])):
        acc['prods'][i] = resolve_product(acc['prods'][i], items)

    with sqlite3.connect('extracts.db') as db_conn:
        guarantee_schema(db_conn)
        curs = db_conn.cursor()
        do_inserts(curs, items, 'item')
        do_inserts(curs, acc['recs'], 'recipe')
        do_inserts(curs, acc['ings'], 'recipe_ingredient')
        do_inserts(curs, acc['prods'], 'recipe_product')

if __name__ == '__main__':
    main(sys.argv[1:])

