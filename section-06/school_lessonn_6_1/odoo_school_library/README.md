Odoo School: Lesson 6-1
-----------------------

Module data and demo data
-------------------------

Master data in `data/`, demo data in `demo/` (XML and CSV).

Demo data is not loaded by default in Odoo 19. To see it, create a new database with the `--with-demo` flag:

```
./odoo-bin -c odoo.conf -d library_demo -i odoo_school_library --with-demo
```

Installation
------------

To install this module, you need to:

1. Clone repository.
2. Add the repository path to the config file.
3. Update the app list.
4. Install the module.
