"""
Program to compare QPE hosts and TDE hosts "apples to apples" with the LEGACY DESI DECam survey
"""
import pickle
import numpy as np
from ned_wright_cosmology import calculate_cosmo
from utils import print_table, myCornerPlot, toLog, myFinalPlot, myCombinedFinalPlot, recombine_arrays, add_0_uncertainties, makeLatexTable, redshiftMass, cut_from_catalog
import matplotlib.pyplot as plt
from paper_data import *
from download_data import *
import sys
import pandas as pd


QPE_and_TDEs = [5] # indices of QPE+TDE hosts which are currently only in the QPE arrays


if __name__ == "__main__":

    # load QPE and TDE data
    qpe_load_0 = np.loadtxt("QPE_allRelevantData_0.txt")
    qpe_load_1 = np.loadtxt("QPE_allRelevantData_1.txt")
    qpe_load_2 = np.loadtxt("QPE_allRelevantData_2.txt")
    QPE_fullData = recombine_arrays(qpe_load_0,qpe_load_1,qpe_load_2)

    included = ""
    if input("Make redshift cut for hammerstein TDEs? [y/n]") == "y":
        included = "zcut_"
        goodGal = [True, True, False, False, True, False, False, False, True, True, False, False, False, True, True, True, False, False, True, False, False, False, False, True, True, False]
        remaining_hammerstein_TDE_names = np.array(remaining_hammerstein_TDE_names)[goodGal]
        remaining_hammerstein_TDE_redshifts = np.array(remaining_hammerstein_TDE_redshifts)[goodGal]

    tde_load_0 = np.loadtxt(f"{included}hammerstein_TDE_allRelevantData_0.txt")
    tde_load_1 = np.loadtxt(f"{included}hammerstein_TDE_allRelevantData_1.txt")
    tde_load_2 = np.loadtxt(f"{included}hammerstein_TDE_allRelevantData_2.txt")
    TDE_fullData = recombine_arrays(tde_load_0,tde_load_1,tde_load_2)
    TDE_fullData = TDE_fullData[:26,:,:]
    if input("Only use the hammerstein2021 TDEs? [y/n]") == "y":
        indices_2021 = []
        for name in hammerstein2021_TDE_names:
            try:
                indices_2021.append(remaining_hammerstein_TDE_names.index(name))
            except:
                pass
        print(indices_2021)
        #TDE_fullData = TDE_fullData[[],:,:]
    # load reference catalog
    refCat = np.loadtxt("referenceCatalog_final.txt")
    fieldnames = [f"col_{i}" for i in range(refCat.shape[1])]
    refCat = pd.read_csv("referenceCatalog_final.txt", delimiter=" ", header=None, names=fieldnames)

    QPE_r50s, TDE_r50s = QPE_fullData[:,5,:], TDE_fullData[:,5,:]
    QPE_sersicIndices, TDE_sersicIndices = QPE_fullData[:,1,:], TDE_fullData[:,1,:]
    QPE_bulgeRatios, TDE_bulgeRatios = QPE_fullData[:,0,:], TDE_fullData[:,0,:]
    QPE_SMSDs, TDE_SMSDs = QPE_fullData[:,2,:], TDE_fullData[:,2,:]
    QPE_stellar_masses, TDE_stellar_masses = QPE_fullData[:,3,:], TDE_fullData[:,3,:]
    QPE_mBH, TDE_mBH = QPE_fullData[:,4,:], TDE_fullData[:,4,:]

    makeLatexTable(np.concatenate((objects_names, remaining_hammerstein_TDE_names)),
                   np.concatenate((QPE_redshifts,remaining_hammerstein_TDE_redshifts)),
                   np.concatenate((QPE_r50s,TDE_r50s)),
                   np.concatenate((QPE_sersicIndices,TDE_sersicIndices)),
                   np.concatenate((QPE_bulgeRatios,TDE_bulgeRatios)),
                   np.concatenate((QPE_SMSDs,TDE_SMSDs)),
                   np.concatenate((QPE_stellar_masses,TDE_stellar_masses)),
                   references="abccefddghijklmnnno",
                   filename="hammerstein_latexTable.txt"
                   )

    QPE_redshifts = add_0_uncertainties(QPE_redshifts)
    remaining_hammerstein_TDE_redshifts = add_0_uncertainties(remaining_hammerstein_TDE_redshifts)

    QPE_data = np.array([QPE_redshifts, QPE_stellar_masses, QPE_mBH])
    TDE_data = np.array([np.concatenate((remaining_hammerstein_TDE_redshifts, QPE_redshifts[QPE_and_TDEs])), np.concatenate((TDE_stellar_masses, QPE_stellar_masses[QPE_and_TDEs])), np.concatenate((TDE_mBH, QPE_mBH[QPE_and_TDEs]))])

    redshiftMass([QPE_data, TDE_data], referenceCatalogData=refCat, columns_compare=(1,63,67), save_plot="ham_redshift_distribution", fontsize=16, markersize=10,
                        levels=[0.5,0.7,0.9,1],
                        smoothness=7,
                        referenceSmoothness=7,
                        bins=10,
                        kernelDensitiesReference=False,
                        extremums={"param": (0.01,0.1),
                                   "m_star": (9.2,10.4),
                                   }
                )

    QPE_data = np.array([QPE_sersicIndices, QPE_bulgeRatios, QPE_SMSDs, QPE_stellar_masses, QPE_mBH])
    TDE_data = np.array([np.concatenate((TDE_sersicIndices, QPE_sersicIndices[QPE_and_TDEs])), np.concatenate((TDE_bulgeRatios, QPE_bulgeRatios[QPE_and_TDEs])), np.concatenate((TDE_SMSDs, QPE_SMSDs[QPE_and_TDEs])), np.concatenate((TDE_stellar_masses, QPE_stellar_masses[QPE_and_TDEs])), np.concatenate((TDE_mBH, QPE_mBH[QPE_and_TDEs]))])
    myCombinedFinalPlot([QPE_data, TDE_data], referenceCatalogData=refCat, columns_compare=((60,12,68),63,67), save_plot="ham_combined_final", fontsize=16, markersize=10,
                        levels=[0.5,0.7,0.9,1],
                        smoothness=12,
                        referenceSmoothness=20,
                        bins=10,
                        kernelDensitiesReference=False,
                        extremums={"n_sersic": (0,5.5),
                                   "bt_ratio": (-0.15,1.05),
                                   "ssmd": (8.2,10.6),
                                   "m_star": (9,11.25),
                                   "m_bh": (4.5,9),
                                   }
                        )

    # Make big plot
    QPE_data  = np.array([QPE_mBH[:,0], QPE_stellar_masses[:,0], QPE_redshifts[:,0], QPE_r50s[:,0], QPE_bulgeRatios[:,0], QPE_sersicIndices[:,0], QPE_SMSDs[:,0]])
    TDE_data = np.array([TDE_mBH[:,0], TDE_stellar_masses[:,0], remaining_hammerstein_TDE_redshifts[:,0], TDE_r50s[:,0], TDE_bulgeRatios[:,0], TDE_sersicIndices[:,0], TDE_SMSDs[:,0]])
    double_hosts_data = QPE_data[:,QPE_and_TDEs]
    TDE_data = np.vstack((TDE_data.T, double_hosts_data.T)).T
    myCornerPlot(
        [QPE_data,TDE_data,double_hosts_data],
        labels=["$\log(M_\mathrm{BH})$", "$\log(M_\star)$", "$z$", "$r_{50}$", "$(B/T)_g$", "$n_\mathrm{Sérsic}$", "$\log(\Sigma_{M_\star})$"],
        units=["$[M_\odot]$", "$[M_\odot]$", " ", "$[\mathrm{kpc}]$", " ", " ", "$[M_\odot/\mathrm{kpc}^2]$"],
        smoothness=6,
        markersize=10,
        levels=[0.5,0.7,0.9,1],
        refCat=refCat,
        columns_compare=[67,63,1,59,12,60,68],
        save_plot="ham_corner_plot",
        extremums={"$\log(M_\mathrm{BH})$": (4.5,9),
                   "$\log(M_\star)$": (9,11.25),
                   "$(B/T)_g$": (-0.15,1.05),
                   "$r_{50}$": (0,10.5),
                   "$n_\mathrm{Sérsic}$": (0,5.5),
                   "$\log(\Sigma_{M_\star})$": (8.2,10.6) 
                   }
        )
