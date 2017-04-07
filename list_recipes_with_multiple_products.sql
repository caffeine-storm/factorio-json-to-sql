select count(recipe.id), recipe.mod_pack, recipe.name from recipe join recipe_product on recipe.id = recipe_product.recipe join item on recipe_product.product = item.rowid group by recipe.id having count(recipe.id) > 1;

