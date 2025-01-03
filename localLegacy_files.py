"""
Program to compare QPE hosts and TDE hosts "apples to apples" with the LEGACY DESI DECam survey
"""
import pickle
import numpy as np
from ned_wright_cosmology import calculate_cosmo
from utils import print_table, myCornerPlot, toLog, myFinalPlot, add_0_uncertainties
import matplotlib.pyplot as plt
from paper_data import *
from download_data import *
import sys
import pandas as pd
#from prospector.prospector_myFits import QPE_stellar_masses_desiProspector, TDE_stellar_masses_desiProspector
#from bulgeRatio import QPE_bulgeRatios, TDE_bulgeRatios

QPE_bulgeRatios, TDE_bulgeRatios = np.loadtxt("QPE_bulgeRatios.txt"), np.loadtxt("TDE_bulgeRatios.txt")

QPE_and_TDEs = [4,5,8]

def get_n_and_r50(objID, model="None", band="i", survey="DESI", redshift=0, qpe_oder_tde="QPE"):
    if qpe_oder_tde == "QPE":
        picklename = f"{objects_names[objID]}_{band}-band_{model}_{survey}.pkl"
    else:
        picklename = f"{TDE_names[objID]}_{band}-band_{model}_{survey}.pkl"
    try:
        fitting_run_result = pickle.load(open("galight_fitruns/big_fits/"+picklename,'rb'))  #fitting_run_result is actually the fit_run in galightFitting.py.
    except:
        fitting_run_result = pickle.load(open("galight_fitruns/"+picklename,'rb'))
    #print(picklename)
    #Calculate the Sersic index + uncertainties
    chain = fitting_run_result.samples_mcmc
    params = fitting_run_result.param_mcmc
    if "R_sersic_lens_light1" in params and "n_sersic_lens_light1" in params:
        lo, mid, hi = np.percentile(chain[:, 7],16), np.percentile(chain[:, 7],50), np.percentile(chain[:, 7],84)
        plus, minus = (hi-mid), (mid-lo)
        sersic_index_data = [mid, minus, plus]

        #Calculate the Sersic half-light radius + uncertainties:
        lo, mid, hi = np.percentile(chain[:, 6],16), np.percentile(chain[:, 6],50), np.percentile(chain[:, 6],84)
        plus, minus = (hi-mid), (mid-lo)
        r50_data = [mid, minus, plus]
    elif "R_sersic_lens_light0" in params and "n_sersic_lens_light0" in params:
        lo, mid, hi = np.percentile(chain[:, 1],16), np.percentile(chain[:, 1],50), np.percentile(chain[:, 1],84)
        plus, minus = (hi-mid), (mid-lo)
        sersic_index_data = [mid, minus, plus]

        #Calculate the Sersic half-light radius + uncertainties:
        lo, mid, hi = np.percentile(chain[:, 0],16), np.percentile(chain[:, 0],50), np.percentile(chain[:, 0],84)
        plus, minus = (hi-mid), (mid-lo)
        r50_data = [mid, minus, plus]
    else:
        #print(qpe_oder_tde)
        sersic_index_data = [fitting_run_result.final_result_galaxy[0]["n_sersic"], 0, 0]
        r50_data = [fitting_run_result.final_result_galaxy[0]["R_sersic"], 0, 0]
    #Convert r50 from arcsec to kpc
    cosmology_params = calculate_cosmo(redshift, H0=67, Omega_m=0.31, Omega_v=0.69)
    kpc_per_arcsec = cosmology_params["kpc_DA"]
    r50_data = np.array(r50_data)*kpc_per_arcsec

    magnitude = fitting_run_result.final_result_galaxy[0]['magnitude']
    # Add the magnitude of the disk if there is a bulge+disk decomposition
    try:
        magnitude = -2.5*np.log10(10**(-0.4*magnitude)+10**(-0.4*fitting_run_result.final_result_galaxy[1]['magnitude']))
    except:
        pass

    return sersic_index_data, r50_data, magnitude



def stellarMassDensity(M_star, r50, returnLog=False):
    '''
    Calculate the stellar surface mass density \Sigma_{M_\ast} from the total stellar mass and the half-light radius

    M_star: stellar mass in solar masses -> tuple/list/array such as (mass, errlo, errhi)
    r50: half-light radius in kpc -> tuple/list/array such as (radius, errlo, errhi)

    returns [value, errlo, errhi]
    '''
    try:
        res = M_star[0]/r50[0]**2
        errlo = res*np.sqrt((M_star[1]/M_star[0])**2+(2*r50[2]/r50[0])**2)
        errhi = res*np.sqrt((M_star[2]/M_star[0])**2+(2*r50[1]/r50[0])**2)
        if returnLog:
            return [np.log10(res), errlo/(res*np.log(10)), errhi/(res*np.log(10))]
        return [res, errlo, errhi]
    except:
        #In the exception where the user did not input uncertainties, the value will still be calculated.
        if returnLog:
            return np.log10(M_star/r50[0]**2)
        return M_star/r50[0]**2#/(2*np.pi) #is there a constant 2pi we need to divide by???

def checkWhichFiltersWork(list_of_dicts, qpe_oder_tde="QPE"):
    working = {"g":[], "r":[], "i":[], "z":[]}
    for i in range(len(list_of_dicts)):
        for band in "griz":
            try:
                idc = list_of_dicts[i][band]
                working[band].append("\x1b[32mY\x1b[0m")
            except:
                working[band].append("\x1b[31mN\x1b[0m")
    names = objects_names if qpe_oder_tde=="QPE" else TDE_names
    print_table(np.array([names, working["g"], working["r"], working["i"], working["z"]]).T,
                header=["Name", "g", "r", "i", "z"],
                title="Working filters",
                borders=2,
                override_length=[15, 1, 1, 1, 1],
                )
    return

def printPropertyAcrossFilters(list_of_dicts, name_of_property="Name of property", round_to_n_decimals=2, qpe_oder_tde="QPE"):
    properties = {"g":[], "r":[], "i":[], "z":[]}
    for i in range(len(list_of_dicts)):
        for band in "griz":
            try:
                properties[band].append(f"{list_of_dicts[i][band][0]:0.2f}")
            except:
                try:
                    properties[band].append(f"{list_of_dicts[i][band]:0.2f}")
                except:
                    properties[band].append("-")
    names = objects_names if qpe_oder_tde=="QPE" else TDE_names
    print_table(np.array([names, properties["g"], properties["r"], properties["i"], properties["z"]]).T,
                header=["Name", "g", "r", "i", "z"],
                title=name_of_property,
                borders=2,
                )
    return










survey = "DESI_PSF"
tde_survey = "DESI_PSF"

#Do this part so other programs can load it (especially the magnitudes from prospector)
#First, load the TDE sersic indices and half-light radii into arrays or list, idc:
QPE_sersicIndices = []
QPE_r50s = []
for i in range(len(objects)):
    QPE_sersicIndices.append({})
    QPE_r50s.append({})
    for band in "griz":
        try:
            n, r50, mag = get_n_and_r50(i, "None", redshift=QPE_redshifts[i], band=band, survey=survey)
            QPE_sersicIndices[-1][band] = n
            QPE_r50s[-1][band] = r50
        except:
            pass



TDE_sersicIndices = []
TDE_r50s = []
for i in range(len(TDE_coords)):
    TDE_sersicIndices.append({})
    TDE_r50s.append({})
    for band in "griz":
        try:
            n, r50, mag = get_n_and_r50(i, "None", redshift=TDE_redshifts[i], band=band, survey=tde_survey, qpe_oder_tde="TDE")
            TDE_sersicIndices[-1][band] = n
            TDE_r50s[-1][band] = r50
        except:
            pass




if __name__ == "__main__":

    #From now on, keep only the r-band properties:
    band_to_keep = "r"
    QPE_placeholder_properties = {"n_sersic":[], "r_50":[]}
    TDE_placeholder_properties = {"n_sersic":[], "r_50":[]}
    for i in range(len(objects)):
        QPE_placeholder_properties["n_sersic"].append(QPE_sersicIndices[i][band_to_keep])
        QPE_placeholder_properties["r_50"].append(QPE_r50s[i][band_to_keep])
    for i in range(len(TDE_coords)):
        try:
            TDE_placeholder_properties["n_sersic"].append(TDE_sersicIndices[i][band_to_keep])
            TDE_placeholder_properties["r_50"].append(TDE_r50s[i][band_to_keep])
        except:
            pass
    QPE_sersicIndices = QPE_placeholder_properties["n_sersic"]
    QPE_r50s = QPE_placeholder_properties["r_50"]
    TDE_sersicIndices = TDE_placeholder_properties["n_sersic"]
    TDE_r50s = TDE_placeholder_properties["r_50"]

    # Get the stellar masses:
    QPE_stellar_masses = np.loadtxt("QPE_stellarMasses.txt")
    TDE_stellar_masses = np.loadtxt("TDE_stellarMasses.txt")

    # Calculate stellar mass surface densities
    QPE_SMSDs = np.array([stellarMassDensity(QPE_stellar_masses[i], QPE_r50s[i]) for i in range(len(objects_names))])
    TDE_SMSDs = np.array([stellarMassDensity(TDE_stellar_masses[i], TDE_r50s[i]) for i in range(len(TDE_names))])

    # Convert the stellar masses, black hole masses and the SSMDs to logbase and numpy arrays:
    QPE_stellar_masses = toLog(QPE_stellar_masses)
    TDE_stellar_masses = toLog(TDE_stellar_masses)
    QPE_SMSDs = toLog(QPE_SMSDs)
    TDE_SMSDs = toLog(TDE_SMSDs)
    QPE_mBH = toLog(QPE_mBH)
    TDE_mBH = toLog(TDE_mBH_litterature)


    #Transform lists into arrays
    QPE_sersicIndices = np.array(QPE_sersicIndices)
    QPE_r50s = np.array(QPE_r50s)
    QPE_mBH = np.array(QPE_mBH)
    TDE_sersicIndices = np.array(TDE_sersicIndices)
    TDE_r50s = np.array(TDE_r50s)
    TDE_mBH = np.array(TDE_mBH)

    # Make data distributions
    QPE_data = np.array([QPE_bulgeRatios, QPE_sersicIndices, QPE_SMSDs, QPE_stellar_masses, QPE_mBH, QPE_r50s]).T
    TDE_data = np.array([np.concatenate((TDE_bulgeRatios, QPE_bulgeRatios[QPE_and_TDEs])), np.concatenate((TDE_sersicIndices, QPE_sersicIndices[QPE_and_TDEs])), np.concatenate((TDE_SMSDs, QPE_SMSDs[QPE_and_TDEs])), np.concatenate((TDE_stellar_masses, QPE_stellar_masses[QPE_and_TDEs])), np.concatenate((add_0_uncertainties(TDE_mBH), QPE_mBH[QPE_and_TDEs])), np.concatenate((TDE_r50s, QPE_r50s[QPE_and_TDEs]))]).T

    #print(TDE_data[2,:,:])
    #print(TDE_data.shape)
    # Need to save it in 3 separate files because "no 3D arrays" :(
    for i in range(3):
        np.savetxt(f"QPE_allRelevantData_{i}.txt", QPE_data[i,:,:])
        np.savetxt(f"TDE_allRelevantData_{i}.txt", TDE_data[i,:,:])