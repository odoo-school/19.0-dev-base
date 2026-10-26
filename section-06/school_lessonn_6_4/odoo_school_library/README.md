Odoo School: Lesson 6-4
-----------------------

Writing tests
-------------

Python unit tests live in `tests/`. The shared test data is created once per class
in `tests/common.py` (`OSLTestCommon`), the test files are split by purpose:

* `test_odoo_school_library_book.py` - master data, sequence, ISBN constraint
* `test_form.py` - `Form`, onchange and `freeze_time`
* `test_access_rights.py` - groups, ACLs and record rules (tag `osl_access`)
* `test_http.py` - `HttpCase` for the `/library/my-books` page (tag `osl_http`)
* `test_translations.py` - Ukrainian messages from `i18n/uk.po`

All test classes are tagged `osl`. Run the tests of the module:

```
./odoo-bin -c odoo.conf -d library -i odoo_school_library --test-tags /odoo_school_library
```

Only the access rights tests, or everything except them:

```
./odoo-bin -c odoo.conf -d library -u odoo_school_library --test-tags osl_access
./odoo-bin -c odoo.conf -d library -u odoo_school_library --test-tags osl,-osl_access
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
