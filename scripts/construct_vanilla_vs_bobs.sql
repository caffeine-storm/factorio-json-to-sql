drop table if exists vanilla_to_bob_recipe;

create table vanilla_to_bob_recipe(
    vanilla_recipe int,
    bob_recipe int,
    FOREIGN KEY(vanilla_recipe) references recipe,
    FOREIGN KEY(bob_recipe) references recipe
);

insert into vanilla_to_bob_recipe select v.id, b.id from recipe as v join recipe as b where v.mod_pack = 'vanilla' and b.mod_pack = 'bobs' and v.name = b.name;

drop table if exists vanilla_to_bob_counts;

create table vanilla_to_bob_counts(
    recipe_name varchar(32),
    item_name varchar(32),
    vanilla_count numeric,
    bob_count numeric
);

insert into vanilla_to_bob_counts select rec.name, (select item.name from item where item.rowid = van_ing.ingredient), van_ing.count, bob_ing.count from vanilla_to_bob_recipe as j join recipe_ingredient as van_ing on van_ing.recipe = j.vanilla_recipe join recipe as rec on rec.id = j.vanilla_recipe join recipe_ingredient as bob_ing on bob_ing.recipe = j.bob_recipe where bob_ing.ingredient = van_ing.ingredient;


