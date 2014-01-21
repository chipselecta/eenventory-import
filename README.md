EEnventory-import
=================

[EEnventory](http://chipselecta.com/eenventory/) a is a Web app for
tracking electronic component inventory.  EEnventory-import is a tool
for importing orders from Digi-Key or Mouser into EEnventory.

Dependencies
------------

EEnventory depends on the following pieces of software:

* Python 2.7
* [wget](https://www.gnu.org/software/wget/)
* [Requests](http://docs.python-requests.org/en/latest/)
* [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
* Firefox
* Firefox [Export Cookies](https://addons.mozilla.org/en-US/firefox/addon/export-cookies/) add-on

Requests and Beautiful Soup can be installed with `pip`, if you have
it.  Just do:

    $ pip install requests
    $ pip install beautifulsoup4

Running EEnventory-import
-------------------------

First, [create](http://chipselecta.com/eenventory/login/) an account
on EEventory.

Then, once you have installed the dependencies, log into Digi-Key
and/or Mouser in Firefox and dump the cookies to a file, like
`cookies.txt`, using Export Cookies.  Then run the tool:

    $ python ./EEnventory-import/import-orders.py -d -m <username> <password> cookies.txt

The `-d` option directs the tool to import orders from Digi-Key, and
similarly `-m` for Mouser.

Known Problems
--------------

EEnventory-import can only scrape the first page of Mouser orders.  To
import other orders, you need explicitly invoke EEnventory-import with
the Mouser order page url using the `-o <order url` option.  There is
probably a similar problem with Digi-Key.

Usage
-----

Here is the full import-orders.py usage:

    usage: import-orders.py [-h] [-m] [-d] [-o ORDER] [-a API_ROOT]
			    username password cookies

    Import orders from Distributor (currently Digi-Key and/or Mouser)

    positional arguments:
      username              EEnventory username
      password              EEnventory password
      cookies               cookie file containing Distributor cookies

    optional arguments:
      -h, --help            show this help message and exit
      -m, --mouser          import orders from Mouser
      -d, --digikey         import orders from Digi-Key
      -o ORDER, --order ORDER
			    URL of order to import
      -a API_ROOT, --api-root API_ROOT
			    root URL of the EEnventory API (no trailing slash)
