import argparse
import api

import utils
import digikey, mouser

parser = argparse.ArgumentParser(description='Import orders from Distributor (currently Digi-Key and/or Mouser)')
parser.add_argument('username', help='EEnventory username')
parser.add_argument('password', help='EEnventory password')
parser.add_argument('-m', '--mouser', action='store_true',
                    help='import orders from Mouser')
parser.add_argument('-d', '--digikey', action='store_true',
                    help='import orders from Digi-Key')
parser.add_argument('-o', '--order', type=str,
                    help='URL of order to import')
parser.add_argument('cookies', help='cookie file containing Distributor cookies')
parser.add_argument('-a', '--api-root', type=str,
                    help='root URL of the EEnventory API (no trailing slash)')

args = parser.parse_args()

api.username = args.username
api.password = args.password
utils.cookies = args.cookies
if args.api_root:
    api.api_root = args.api_root

if not args.digikey and not args.mouser:
    print 'Nothing to do; neither -m or -d given.  Exiting.'
    exit()

if args.mouser:
    if args.order:
        mouser.import_order(args.order)
    else:
        mouser.import_orders()
if args.digikey:
    if args.order:
        digikey.import_order(args.order)
    else:
        digikey.import_orders()
