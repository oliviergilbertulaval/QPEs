'''
File to organize the data retrieved from the litterature and simplify the code in other files (i.e. compareModels.py)
'''

import numpy as np
import pandas as pd

# Load TDE host galaxies black hole masses and Sérsic indices:
data = np.array(pd.read_csv("data/TDEsersic_mBH.csv"))
TDE_mBH = 10**data[:,0]
TDE_sersicIndices = data[:,1]

# log(Surface stellar densities) for the 10 TDE hosts used in Law-Smith paper, as found in the Graur paper. My own calculations of the stellar mass surface densities approximately
# give me the same thing as the Graur paper result, which is a good sanity check.
TDE_stellarDensities = [
                (9.5, 0.2, 0.2), #ASASSN-14ae
                (10.1, 0.2, 0.2), #ASASSN-14li
                (9.2, 0.3, 0.2), #PTF-09ge
                (9.5, 0.2, 0.2), #RBS 1032
                (9.5, 0.2, 0.2), #SDSS J1323
                (9.5, 0.2, 0.2), #SDSS J0748
                (9.7, 0.2, 0.3), #SDSS J1342
                (9.3, 0.3, 0.3), #SDSS J1350
                (10.4, "upper limit", "upper limit"), #SDSS J0952
                (9.5, 0.3, 0.2), #SDSS J1201
                ]

#redshifts
QPE_redshifts = [
                (0.018),                                # GSN 069
                (0.02358),                              # RX J1301.9+2747
                (0.0505),                               # eRO-QPE1
                (0.0175),                               # eRO-QPE2
                (0.088),                                # AT 2019vcb
                (0.0186),                               # 2MASX J0249
                (0.024),                                # eRO-QPE3
                (0.044),                                # eRO-QPE4
                (0.0151),                               # AT 2019qiz
                ]

TDE_redshifts = [
                (0.0206),            #ASASSN-14li
                (0.064),            #PTF-09ge
                (0.0436),           #ASASSN-14ae
                ]


#M_BH in solar masses
QPE_mBH = [
                (4E5, 0, 0),                                    # GSN 069
                (1.8E6, 0.1E6, 0.1E6),                          # RX J1301.9+2747
                (4E6, 0, 0),                                    # eRO-QPE1
                (3E6, 0, 0),                                    # eRO-QPE2
                (6.5E6, 1.5E6, 1.5E6),                          # AT 2019vcb
                (8.5E4, 0, 0),#or 5E5 depending on paper        # 2MASX J0249
                (5.3E6, 3.5E6, 0.7E6),                          # eRO-QPE3
                (6.8E7, 3.2E7, 4.8E7),                          # eRO-QPE4
                (1E6, 0, 0),                                    # AT 2019qiz
            ]


#M_star in solar masses
QPE_stellar_masses = [
                (None),                             # GSN 069
                (None),                             # RX J1301.9+2747
                (3.8E9, 1.9E9, 0.4E9),              # eRO-QPE1
                (1.01E9, 0.5E9, 0.01E9),            # eRO-QPE2
                (None),                             # AT 2019vcb
                (None),                             # 2MASX J0249
                (2.56E9, 1.40E9, 0.24E9),           # eRO-QPE3
                (1.6E10, 0.6E10, 0.7E10),           # eRO-QPE4
                (None),                             # AT 2019qiz
                ]

TDE_stellar_masses = [
                (10**9.3, 10**9.3-10**9.2, 10**9.4-10**9.3),                                #ASASSN-14li
                (10**9.87, 10**9.87-10**(9.87-0.17), 10**(9.87+0.13)-10**9.87),             #PTF-09ge
                (10**9.73, 10**9.73-10**(9.73-0.13), 10**(9.73+0.13)-10**9.73),           #ASASSN-14ae
                ]