drop table if exists vanilla_to_marathon_recipe;

create table vanilla_to_marathon_recipe(
    vanilla_recipe int,
    marathon_recipe int,
    FOREIGN KEY(vanilla_recipe) references recipe,
    FOREIGN KEY(marathon_recipe) references recipe
);

insert into vanilla_to_marathon_recipe select v.id, m.id from recipe as v join recipe as m where v.mod_pack = 'vanilla' and m.mod_pack = 'marathon' and v.name = m.name;

drop table if exists vanilla_to_marathon_counts;

create table vanilla_to_marathon_counts(
    recipe_name varchar(32),
    item_name varchar(32),
    vanilla_count numeric,
    marathon_count numeric
);

insert into vanilla_to_marathon_counts select rec.name, (select item.name from item where item.rowid = van_ing.ingredient), van_ing.count, mar_ing.count from vanilla_to_marathon_recipe as j join recipe_ingredient as van_ing on van_ing.recipe = j.vanilla_recipe join recipe as rec on rec.id = j.vanilla_recipe join recipe_ingredient as mar_ing on mar_ing.recipe = j.marathon_recipe where mar_ing.ingredient = van_ing.ingredient;

