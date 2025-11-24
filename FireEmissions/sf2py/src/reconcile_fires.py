#!/usr/bin/env python3

import sys
from database import DataBase
from reconcile import *
from exports import *

config = sys.argv[1]
#db = DataBase('config/pg.json')
#db = DataBase('config/pg_2023_nrt.json')
db = DataBase('config/pg_2024.json')
a = Reconciliation(config, db)
a.purge_events(db)
a.reconcile(db)
a = Export(config, db)
a.export(db)
#a.export_hms(db) ## Bug: This function does not exist anywhere
