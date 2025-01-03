#Load the saved fitting class, the fitting_run_result would be the loaded as fit_run() in previous fittings.
import pickle
import numpy as np
from galight_modif.tools.plot_tools import total_compare
from download_data import objects
import matplotlib.pyplot as plt
import copy
from matplotlib.colors import LogNorm
import matplotlib
my_cmap = copy.copy(matplotlib.cm.get_cmap('gist_heat')) # copy the default cmap
my_cmap.set_bad('black')

def loadRun(ra_dec, type="AGN", band="i", picklename=None):
    if type in ["AGN", "agn", "Agn"]:
        type = "AGN"
    elif type in ["Bulge", "BULGE", "bulge"]:
        type = "Bulge"
    elif type in ["Bulge+AGN", "Bulge+Agn", "BULGE+AGN", "bulge+agn", "AGN+Bulge", "Agn+Bulge", "AGN+BULGE", "agn+bulge"]:
        type = "Bulge+AGN"
    elif type in ["None", "Sersic", "none", "sersic", "single", ""]:
        type = "None"
    else:
        raise ValueError(f"type {type} is not a supported fitting type")
    
    if band in ["g", "G"]:
        band = "g"
        central_wav = 4730 #\AA
    elif band in ["r", "R"]:
        band = "r"
        central_wav = 6420 #\AA
    elif band in ["i", "I"]:
        band = "i"
        central_wav = 7840 #\AA
    elif band in ["z", "Z"]:
        band = "z"
        central_wav = 9260 #\AA
    else:
        raise ValueError(f"band {band} is not a supported filter band")

    if picklename == None:
        picklename = f'ra{str(ra_dec[0])}_dec{str(ra_dec[1])}_{type}_{band}.pkl'
    try:
        fitting_run_result = pickle.load(open("galight_fitruns/big_fits/"+picklename,'rb'))  #fitting_run_result is actually the fit_run in galightFitting.py.
    except:
        fitting_run_result = pickle.load(open("galight_fitruns/"+picklename,'rb'))  #fitting_run_result is actually the fit_run in galightFitting.py.

    try:
        pixel_scale = fitting_run_result.coolinfo["pixel_scale"]
        for i in range(len(fitting_run_result.coolinfo)):
            print(fitting_run_result.coolinfo[i])
    except:
        pixel_scale = 0.262 #Default value for almost all of the runs anyway
        print("No informations on the original fitting parameters used was stored! Running the fit again will solve this.")
    if len(fitting_run_result.image_host_list) == 2:
        print(fitting_run_result.final_result_galaxy[0]["n_sersic"], "vs", fitting_run_result.final_result_galaxy[1]["n_sersic"])
        if fitting_run_result.final_result_galaxy[0]["n_sersic"] < fitting_run_result.final_result_galaxy[1]["n_sersic"]:
            placeholder = copy.deepcopy(fitting_run_result.final_result_galaxy[0])
            fitting_run_result.final_result_galaxy[0] = copy.deepcopy(fitting_run_result.final_result_galaxy[1])
            fitting_run_result.final_result_galaxy[1] = placeholder
            placeholder2 = copy.deepcopy(fitting_run_result.image_host_list[0])
            fitting_run_result.image_host_list[0] = copy.deepcopy(fitting_run_result.image_host_list[1])
            fitting_run_result.image_host_list[1] = placeholder2
        print(fitting_run_result.final_result_galaxy[0]["n_sersic"], "vs", fitting_run_result.final_result_galaxy[1]["n_sersic"])
    print(fitting_run_result.final_result_galaxy[0])
    print("Flux of galaxy:", fitting_run_result.final_result_galaxy[0]['flux_sersic_model'])
    flux_density = copy.copy(fitting_run_result.final_result_galaxy[0]['flux_sersic_model']) #erg/s/cm2/Hz
    # We want to convert this to a flux in erg/s/cm2
    frequency = 299792458/(central_wav/(1E10))
    flux = flux_density*frequency
    #Calculate a magnitude:
    mag = fitting_run_result.zp-2.5*np.log10(flux)
    print("Magnitude of galaxy:", mag)
    print(fitting_run_result.zp)
    print("Magnitude of galaxy:", fitting_run_result.final_result_galaxy[0]['magnitude'])
    #fitting_run_result.run_diag() #dont really care about this one, so leave it commented out unless it suddenly becomes interesting
    #fitting_run_result.model_plot() #same here
    fitting_run_result.mcmc_result_range()
    if fitting_run_result.fitting_kwargs_list[-1][0] == 'MCMC':
        print(np.shape(fitting_run_result.samples_mcmc))
        samples = np.array(fitting_run_result.samples_mcmc).T
        for sample in samples:
            plt.plot(sample)
        plt.xlabel("n step", fontsize=17)
        plt.ylabel("Parameter position", fontsize=17)
        plt.yscale("log")
        plt.title(picklename, fontsize=17)
        plt.show()
        try:
            fitting_run_result.run_diag()
            fitting_run_result.plot_params_corner()
            fitting_run_result.plot_flux_corner()
        except:
            pass
    print("-------------------------------------------------------")
    print("max likelihood:", fitting_run_result.fitting_seq.best_fit_likelihood)
    print("BIC:", fitting_run_result.fitting_seq.bic)
    print("-------------------------------------------------------")

    data = fitting_run_result.fitting_specify_class.kwargs_data['image_data']
    noise = fitting_run_result.fitting_specify_class.kwargs_data['noise_map']
    galaxy_list = fitting_run_result.image_host_list
    ps_list = fitting_run_result.image_ps_list
    galaxy_total_image = np.zeros_like(galaxy_list[0])
    print("Number of galaxies:", len(galaxy_list))
    print("Number of point sources:", len(ps_list))

    for i in range(len(galaxy_list)):
        galaxy_total_image = galaxy_total_image+galaxy_list[i]
    for i in range(len(ps_list)):
        galaxy_total_image = galaxy_total_image+ps_list[i]
    model = galaxy_total_image
    norm_residual = (data - model)/noise
    flux_list_2d = [data, model, norm_residual]
    label_list_2d = ['data', 'model', 'normalized residual']
    if type == "AGN":
        flux_list_1d = [data, model, ps_list[0], galaxy_list[0], -model]
        label_list_1d = ['data', 'model', 'AGN', 'galaxy']
    elif type == "Bulge":
        flux_list_1d = [data, model, galaxy_list[0], galaxy_list[1], -model]
        label_list_1d = ['data', 'model', 'bulge', 'disk']
    elif type == "Bulge+AGN":
        flux_list_1d = [data, model, ps_list[0], galaxy_list[0], galaxy_list[1], -model]
        label_list_1d = ['data', 'model', 'AGN', 'bulge', 'disk']
    elif type == "None":
        flux_list_1d = [data, model, galaxy_list[0], -model]
        label_list_1d = ['data', 'model', 'Sérsic']
    symbol = "+" if ra_dec[1] > 0 else ""
    #Sanity check to verify that galight DOES give us the Half-light Sérsic radius in arcsec (")
    #chain = fitting_run_result.samples_mcmc
    #halfLightSersicRadius = np.percentile(chain[:, 0],50)
    #shapeOfImage = flux_list_2d[1].shape
    ##smallSquareSize = int(np.round(halfLightSersicRadius/np.sqrt(2)/0.262))
    #bigSquareSize = int(np.round(halfLightSersicRadius/0.262))
    #print("Square sizes:", smallSquareSize, bigSquareSize)
    #smallFlux = np.sum(flux_list_2d[1][int(shapeOfImage[0]/2)-smallSquareSize:int(shapeOfImage[0]/2)+smallSquareSize,int(shapeOfImage[0]/2)-smallSquareSize:int(shapeOfImage[0]/2)+smallSquareSize])
    #bigFlux = np.sum(flux_list_2d[1][int(shapeOfImage[0]/2)-bigSquareSize:int(shapeOfImage[0]/2)+bigSquareSize,int(shapeOfImage[0]/2)-bigSquareSize:int(shapeOfImage[0]/2)+bigSquareSize])
    #smallDensity = smallFlux/(2*smallSquareSize)**2
    #bigDensity = bigFlux/(2*bigSquareSize)**2
    #densityInsideCutout = (bigFlux-smallFlux)/((2*bigSquareSize)**2-(2*smallSquareSize)**2)

    #fluxInsideRadius = smallFlux + (halfLightSersicRadius/0.262)**2*(np.pi-2)*densityInsideCutout
    
    #Calculated analytically an approximation that the flux in the Sérsic radius is around (pi/4)*smallFlux+(2/pi)*bigFlux
    #print("Total flux:", np.sum(flux_list_2d[1]))
    #print(f"Flux inside a {squareSize}x{squareSize} square centered:", np.sum(flux_list_2d[1][int(shapeOfImage[0]/2)-squareSize:int(shapeOfImage[0]/2)+squareSize,int(shapeOfImage[0]/2)-squareSize:int(shapeOfImage[0]/2)+squareSize]))
    #print(f"Ratio of flux inside a Sérsic radius to total flux is approximately:", (fluxInsideRadius)/np.sum(flux_list_2d[1]))
    if len(galaxy_list) == 2:
        ax1 = plt.subplot(121)
        ax2 = plt.subplot(122, sharex=ax1, sharey=ax1)
        ax1.imshow(galaxy_list[0],cmap=my_cmap, norm=LogNorm(), origin="lower")
        ax1.set_title("Bulge", fontsize=16)
        ax2.imshow(galaxy_list[1],cmap=my_cmap, norm=LogNorm(), origin="lower")
        ax2.set_title("Disk", fontsize=16)
        plt.show()
    plt.imshow(flux_list_2d[1], origin='lower',cmap=my_cmap, norm=LogNorm())
    plt.title("Model", fontsize=16)
    plt.show()
    if False: #Not sure why this doesn't work anymore, it used to
        total_compare(flux_list_2d, label_list_2d, flux_list_1d, label_list_1d, deltaPix = fitting_run_result.fitting_specify_class.deltaPix,
                            zp=fitting_run_result.zp, if_annuli=False, arrows= False, show_plot = True, mask_image = fitting_run_result.fitting_specify_class.kwargs_likelihood['image_likelihood_mask_list'][0],
                            target_ID = f'{str(ra_dec[0])+symbol+str(ra_dec[1])}-{band}', sum_rest = True)
    #fitting_run_result.plot_final_qso_fit(target_ID = f'{str(ra_dec[0])+symbol+str(ra_dec[1])}-{band}')



    from galight_modif.fitting_process import ModelPlot
    data = fitting_run_result.fitting_specify_class.kwargs_data['image_data']
    if 'psf_error_map' in fitting_run_result.fitting_specify_class.kwargs_psf.keys():
        _modelPlot = ModelPlot(fitting_run_result.fitting_specify_class.kwargs_data_joint['multi_band_list'],
                                fitting_run_result.fitting_specify_class.kwargs_model, fitting_run_result.kwargs_result,
                                arrow_size=0.02, cmap_string="gist_heat", 
                                image_likelihood_mask_list=fitting_run_result.fitting_specify_class.kwargs_likelihood['image_likelihood_mask_list'] )    
        _, psf_error_map, _, _ = _modelPlot._imageModel.image_linear_solve(inv_bool=True, **fitting_run_result.kwargs_result)
        noise = np.sqrt(fitting_run_result.fitting_specify_class.kwargs_data['noise_map']**2+np.abs(psf_error_map[0]))
    else:
        noise = fitting_run_result.fitting_specify_class.kwargs_data['noise_map']
    
    ps_list = fitting_run_result.image_ps_list

    ps_image = np.zeros_like(data)
    target_ID = f'{str(ra_dec[0])+symbol+str(ra_dec[1])}-{band}'
    for i in range(len(ps_list)):
        ps_image = ps_image+ps_list[i]
    galaxy_list = fitting_run_result.image_host_list
    galaxy_image = np.zeros_like(data)
    for i in range(len(galaxy_list)):
        galaxy_image = galaxy_image+galaxy_list[i]
    model = ps_image + galaxy_image
    data_removePSF = data - ps_image
    norm_residual = (data - model)/noise
    if len(ps_list) != 0: #If there is an AGN
        flux_dict_2d = {'data':data, 'model':model, 'normalized residual':norm_residual}
        flux_dict_1d = {'data':data, 'model':model, 'AGN':ps_image, 'Sérsic':galaxy_image}
        if len(galaxy_list) == 2:
            flux_dict_1d = {'data':data, 'model':model, 'AGN':ps_image, 'Bulge':galaxy_list[0], 'Disk':galaxy_list[1]}
        total_compare(list(flux_dict_2d.values()), list(flux_dict_2d.keys()), list(flux_dict_1d.values()), list(flux_dict_1d.keys()), deltaPix = fitting_run_result.fitting_specify_class.deltaPix,
                        zp=fitting_run_result.zp, if_annuli=False,
                        mask_image = fitting_run_result.fitting_specify_class.kwargs_likelihood['image_likelihood_mask_list'][0],
                        target_ID = target_ID, cmap=my_cmap, center_pos= [-fitting_run_result.final_result_ps[0]['ra_image'][0]/fitting_run_result.fitting_specify_class.deltaPix, 
                                                                        fitting_run_result.final_result_ps[0]['dec_image'][0]/fitting_run_result.fitting_specify_class.deltaPix], figsize=(13,4.5) )
    else: #If there is no AGN
        flux_dict_2d = {'data':data, 'model':model, 'normalized residual':norm_residual}
        flux_dict_1d = {'data':data, 'model':model, 'Sérsic':galaxy_image}
        if len(galaxy_list) == 2:
            flux_dict_1d = {'data':data, 'model':model, 'Bulge':galaxy_list[0], 'Disk':galaxy_list[1]}
        total_compare(list(flux_dict_2d.values()), list(flux_dict_2d.keys()), list(flux_dict_1d.values()), list(flux_dict_1d.keys()), deltaPix = fitting_run_result.fitting_specify_class.deltaPix,
                        zp=fitting_run_result.zp, if_annuli=False,
                        mask_image = fitting_run_result.fitting_specify_class.kwargs_likelihood['image_likelihood_mask_list'][0],
                        target_ID = target_ID, cmap=my_cmap, figsize=(13,4.5))
    #flux_dict_2d['data-point source'] = flux_dict_2d.pop('data$-$point source')
    fitting_run_result.flux_2d_out = flux_dict_2d
    fitting_run_result.flux_1d_out = flux_dict_1d
    plt.show()

    import sys
    sys.exit()
    fitting_run_result.fitting_specify_class.plot_fitting_sets()
    obj_id = int(input('Which component to measure using statmorph?\n'))
    morph = fitting_run_result.cal_statmorph(obj_id=obj_id, segm=fitting_run_result.fitting_specify_class.segm_deblend , if_plot = True)


    from statmorph.utils.image_diagnostics import make_figure
    fig = make_figure(morph)
    plt.show()
    print('xc_asymmetry =', morph.xc_asymmetry)
    print('yc_asymmetry =', morph.yc_asymmetry)
    print('ellipticity_asymmetry =', morph.ellipticity_asymmetry)
    print('elongation_asymmetry =', morph.elongation_asymmetry)
    print('orientation_asymmetry =', morph.orientation_asymmetry)
    print('C =', morph.concentration)
    print('A =', morph.asymmetry)
    print('S =', morph.smoothness)


from download_data import objects, comparisons, objects_names, objects_types, TDE_names, TDE_coords, TDE_types, hammerstein_TDE_coords, hammerstein_TDE_names, french_TDE_names, french_TDE_coords


if input("Load French TDE host bulge+disk fit? [y/n]") == "y":
    for i, name in enumerate(french_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(french_TDE_names)-1}]:\n"))
    loadRun(french_TDE_coords[objID], type="Bulge", band="g", picklename=f"{french_TDE_names[objID]}_{'g'}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load French TDE host bulge+disk fit other bands? [y/n]") == "y":
    for i, name in enumerate(french_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(french_TDE_names)-1}]:\n"))
    band = input("which band? [griz]")
    loadRun(french_TDE_coords[objID], type="Bulge", band=band, picklename=f"{french_TDE_names[objID]}_{band}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load French TDE host single-sersic fit? [y/n]") == "y":
    for i, name in enumerate(french_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(french_TDE_names)-1}]:\n"))
    band = input("Which band? [griz]")
    loadRun(french_TDE_coords[objID], type="None", band=band, picklename=f"{french_TDE_names[objID]}_{band}-band_{'None'}_DESI_PSF.pkl")

elif input("Load Hammerstein TDE host bulge+disk fit? [y/n]") == "y":
    for i, name in enumerate(hammerstein_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(hammerstein_TDE_names)-1}]:\n"))
    loadRun(hammerstein_TDE_coords[objID], type="Bulge", band="g", picklename=f"{hammerstein_TDE_names[objID]}_{'g'}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load Hammerstein TDE host bulge+disk fit other bands? [y/n]") == "y":
    for i, name in enumerate(hammerstein_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(hammerstein_TDE_names)-1}]:\n"))
    band = input("which band? [griz]")
    loadRun(hammerstein_TDE_coords[objID], type="Bulge", band=band, picklename=f"{hammerstein_TDE_names[objID]}_{band}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load Hammerstein TDE host single-sersic fit? [y/n]") == "y":
    for i, name in enumerate(hammerstein_TDE_names):
        print(i,":",name)
    objID = int(input(f"Enter the object ID you want to load [0-{len(hammerstein_TDE_names)-1}]:\n"))
    extension = input("If there is an extension name to the pickle file type it here, otherwise press Enter:")
    if extension != "":
        extension = "_"+extension
    loadRun(hammerstein_TDE_coords[objID], type="None", band="r", picklename=f"{hammerstein_TDE_names[objID]}_{'r'}-band_{'None'}_DESI_PSF{extension}.pkl")

elif input("Load FINAL2 BULGE QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    loadRun(objects[objID], type="None", band="g", picklename=f"{objects_names[objID]}_{band}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load FINAL2 BULGE TDE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(TDE_coords)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    loadRun(TDE_coords[objID], type="None", band="g", picklename=f"{TDE_names[objID]}_{band}-band_{'Bulge'}_DESI_PSF_FINAL2.pkl")

elif input("Load FINAL BULGE QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    loadRun(objects[objID], type="None", band="g", picklename=f"{objects_names[objID]}_{'g'}-band_{'Bulge'}_DESI_PSF_FINAL.pkl")

elif input("Load FINAL BULGE TDE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(TDE_coords)-1}]:\n"))
    loadRun(TDE_coords[objID], type="None", band="g", picklename=f"{TDE_names[objID]}_{'g'}-band_{'Bulge'}_DESI_PSF_FINAL.pkl")

elif input("Load CO-ADDED SURVEY_PSF QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    model = input("Which model do you want to load?\n")
    loadRun(objects[objID], type="None", band=band, picklename=f"{objects_names[objID]}_{band}-band_{model}_DESI_PSF.pkl")

elif input("Load CO-ADDED SURVEY_PSF TDE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(TDE_coords)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    model = input("Which model do you want to load?\n")
    loadRun(TDE_coords[objID], type="None", band=band, picklename=f"{TDE_names[objID]}_{band}-band_{model}_DESI_PSF.pkl")

elif input("Load CO-ADDED TDE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    loadRun(TDE_coords[objID], type="None", band=band, picklename=f"{TDE_names[objID]}_{band}-band_{TDE_types[objID]}_DESI.pkl")

elif input("Load CO-ADDED QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    loadRun(objects[objID], type=objects_types[objID], band=band, picklename=f"{objects_names[objID]}_{band}-band_{objects_types[objID]}_DESI.pkl")

elif input("Load PANSTARRS QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = "r"
    loadRun(objects[objID], type=objects_types[objID], band=band, picklename=f"{objects_names[objID]}_{band}-band_{objects_types[objID]}_PANSTARRS.pkl")

elif input("Load QPE host? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(objects)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    type = input("Enter the type of extra-component fitting you want to load [None, AGN, Bulge, Bulge+AGN]:\n")
    loadRun(objects[objID], type=type, band=band)

elif input("Load TDE host r-band raw? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(TDE_coords)-1}]:\n"))
    band = "r"
    type = "None"
    survey = "DESI"
    picklename = f"{TDE_names[objID]}_{band}-band_{type}_{survey}_raw.pkl"
    loadRun(TDE_coords[objID], type=type, band=band, picklename=picklename)

elif input("Load TDE host (outdated)? [y/n]") == "y":
    objID = int(input(f"Enter the object ID you want to load [0-{len(comparisons)-1}]:\n"))
    band = input("Enter the filter band you want to load [g,r,i,z]:\n")
    type = input("Enter the type of extra-component fitting you want to load [None, AGN, Bulge, Bulge+AGN]:\n")
    picklename = f'ra{str(comparisons[objID][0])}_dec{str(comparisons[objID][1])}_{type}_{band}.pkl'
    add = input("Additional suffix?\n")
    if add != "":
        picklename = f'ra{str(comparisons[objID][0])}_dec{str(comparisons[objID][1])}_{type}_{band}_{add}.pkl'
    loadRun(comparisons[objID], type=type, band=band, picklename=picklename)