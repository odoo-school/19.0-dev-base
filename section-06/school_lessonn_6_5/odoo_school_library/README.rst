===================
Odoo School Library
===================

Library management for the Odoo School course "Odoo Development Base",
section 6 "Module formalization", lesson 6-5 "Adding documentation".

The module keeps a catalogue of books with inventory numbers, issues books
to readers, separates librarians from library administrators, and schedules
activities for publication anniversaries. Readers see their books on the
``/library/my-books`` page.

Installation
============

To install this module, you need to:

#. Clone the repository.
#. Add the repository path to the ``addons_path`` of the config file.
#. Update the apps list.
#. Install the module.

Configuration
=============

To give a user access to the library, you need to:

#. Go to **Settings** > **Users & Companies** > **Users**.
#. Open the user and choose **Librarian** or **Administrator** in the **Library** field.

The scheduled action **Library: Publication anniversaries** runs on the first
day of every month. It can be changed in **Settings** > **Technical** >
**Scheduled Actions** (developer mode).

Usage
=====

To manage the books, you need to:

#. Go to **Library** > **Catalog** > **Books**.
#. Create a book, set the reader and click **Take Book**.
#. Use **Write Off** to archive a book (library administrators only).

Notes
-----

* Demo librarians (demo database only): ``olena`` / ``olena`` and ``taras`` / ``taras``.
* Run the tests with ``--test-tags /odoo_school_library``.

Changelog
=========

See ``doc/changelog.rst``.

Credits
=======

Authors
-------

* Odoo School

Website
-------

* https://odoo.school/
