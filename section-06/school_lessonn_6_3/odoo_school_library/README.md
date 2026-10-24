Odoo School: Lesson 6-3
-----------------------

Translations: creation and verification
---------------------------------------

All source terms are written in English (en_US). Ukrainian translations live in `i18n/uk.po`,
the template for new languages is `i18n/odoo_school_library.pot`.

Regenerate both files (the module must be installed and Ukrainian activated):

```
./odoo-bin i18n export -c odoo.conf -d library odoo_school_library -l pot uk
```

Demo librarians (demo database only, created with `--with-demo`):

* login `olena`, password `olena`
* login `taras`, password `taras`

Installation
------------

To install this module, you need to:

1. Clone repository.
2. Add the repository path to the config file.
3. Update the app list.
4. Install the module.
