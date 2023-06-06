#!/usr/bin/env python3
'''
Stefan Lohmaier <stefan@slohmaier.de>, hereby disclaims all copyright interest in the program “mintoscsv2parqetcsv” (which deconstructs trees) written by James Hacker.
---
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''
import argparse
import csv
import os
import re
import sys

_TYPEMAP = {
    'Kauf': 'Buy',
    'Verkauf': 'Sell',
}

def parse_amount(amount: str):
    return '{:.6f}'.format(float(amount)).replace('-', '')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser('mintoscsv2parqetcsv',
        description='Convert ebase Umsatz CSV\'s to Parqet CSV\'s.')
    argparser.add_argument('--ecsv', '-e', dest='ecsv', required=True,
        help='path to ebase Umsatz CSV')
    argparser.add_argument('--pcsv', '-p', dest='pcsv', required=True,
        help='output path for Parqet Cash CSV')

    args = argparser.parse_args()
    #fod code completion
    args.ecsv = args.ecsv
    args.pcsv = args.pcsv
    
    if not os.path.isfile(args.ecsv):
        sys.stderr.write('ebase Umsatz CSV "{0}" is not a file! Try {1} -h.\n'
            .format(args.ecsv, sys.argv[0]))
        sys.exit(1)
    
    ecsvFile = open(args.ecsv, 'r', encoding='latin-1')
    ecsv = csv.reader(ecsvFile, delimiter=';')

    rows = []
    for row in ecsv:
        #add 20 to dd.mm.yy before yy
        date = row[3].split('.')
        if len(date) != 3:
            continue
        date[2] = '20'+date[2]
        date = '.'.join(date)
        
        _type = _TYPEMAP.get(row[4], row[4])
        isin = row[7]
        currency = row[9]
        fee = '0'
        parts = row[10].replace(',', '.')
        amount = row[8].replace(',', '.')
        tax = row[29].replace(',', '.')

        value = row[18].replace(',', '.')
        kurs = row[11].replace(',', '.')
        fee = '0'
        value = str(float(parts)*float(kurs))

        if _type in ['Verkauf wegen Vorabpauschale', 'Entgeltbelastung Verkauf', 'Entgelt Verkauf']:
            amount = str(float(kurs) * float(parts))
            fee = amount
            tax = '0'
            _type = 'Sell'
        if not _type in _TYPEMAP.values():
            raise ValueError(_type)

        rows.append([date, parse_amount(fee), isin, parse_amount(kurs), parse_amount(parts), parse_amount(tax), _type, parse_amount(amount)])

    pcsvFile = open(args.pcsv, 'w+')
    pcsv = csv.writer(pcsvFile, 'unix', quoting=0, delimiter=';')
    pcsv.writerow(['date', 'fee', 'isin', 'price', 'shares', 'tax', 'type', 'amount'])

    for row in rows:
        pcsv.writerow(row)

    ecsvFile.close()
    pcsvFile.close()
