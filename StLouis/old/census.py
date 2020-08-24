# Daniel Van Hoesen
# CensusData API for Python
# Created: 07/12/2020


####################
## Imports
####################

import pandas as pd
import censusdata as cd
import statsmodels.formula.api as sm

stl = cd.censusgeo(['Missouri'])

data = cd.download.download('acs1', 2012, stl, var, key=None, tabletype='detail', endpt='')