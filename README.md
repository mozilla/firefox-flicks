Firefox Flicks
==============
Firefox Flicks is a [playdoh][gh-playdoh]-based site that allows users to submit
vidoes and view other entries in the Firefox Flicks contest.

[gh-playdoh]: https://github.com/mozilla/playdoh


Setup
-----
These instructions assume you have [git][], [python][], and `pip` installed. If
you don't have `pip` installed, you can install it with `easy_install pip`.

1. Start by getting the source:

   ```sh
   $ git clone --recursive git://github.com/mozilla/firefox-flicks.git
   $ cd firefox-flicks
   ```

2. Create a virtualenv for Flicks. Skip the first step if you already have
   `virtualenv` installed.

   ```sh
   $ pip install virtualenv
   $ virtualenv venv
   $ source venv/bin/activate
   ```

3. Install the compiled requirements:

   ```sh
   $ pip install -r requirements/compiled.txt
   ```

4. Set up a local MySQL database. The [MySQL Installation Documentation][mysql]
   explains how to do this.

5. Configure your local settings by copying `flicks/settings/local.py-dist` to
   `flicks/settings/local.py` and customizing the settings in it:

   ```sh
   $ cp settings/local.py-dist settings/local.py
   ```

   The file is commented to explain what each setting does and how to customize
   them.

6. Initialize your database structure:

   ```sh
   $ python manage.py syncdb
   $ python manage.py migrate
   ```

7. Install translations from SVN into the `firefox-flicks/locale` directory:

   ```sh
   $ git svn clone https://svn.mozilla.org/projects/l10n-misc/trunk/firefoxflicks/locale/ locale
   # or
   $ svn checkout https://svn.mozilla.org/projects/l10n-misc/trunk/firefoxflicks/locale/ locale
   ```

8. Install the GNU version of `gettext`. If you are on OSX, you can do this
   using [Homebrew][]:

   ```sh
   $ brew install gettext
   $ brew link gettext
   ```

9. Compile the translations:

   ```sh
   $ python manage.py compilemessages
   ```

[git]: http://git-scm.com/
[python]: http://www.python.org/
[mysql]: http://dev.mysql.com/doc/refman/5.6/en/installing.html
[Homebrew]: http://mxcl.github.com/homebrew/


Running the Development Server
------------------------------
You can launch the development server like so:

```sh
$ python manage.py runserver
```


Waffle Flags
------------
The following [waffle][] flags are in use:

* `winners_page` - Controls whether the winners page is available, as well as
  displaying winner information on designated videos.

[waffle]: https://github.com/jsocol/django-waffle


License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

