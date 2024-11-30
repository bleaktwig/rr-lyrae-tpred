# --+ Preamble +----------------------------------------------------------------
import os, random
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import voigt_profile
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup plotting params.
plt.rcParams['figure.figsize'] = (7, 4)
sns.set_theme()

# --+ Setup +-------------------------------------------------------------------
# Constants.
PATH_SYNTHETIC = "../../spectra/synthetic"
PATH_REAL      = "../../spectra/real"
PATH_PLOTS     = "plots"
COL_LABELS = ["wavelength", "flux", "flux err"]
COL_UNITS  = ["nm", "", ""]

def voigt(x, amp, center, sigma, gamma):
    return amp * voigt_profile(x - center, sigma, gamma)

# --+ Code +--------------------------------------------------------------------
# TODO.
#   * Iterate through the whole input folder, storing the errors in a dict and
#     the plots in a particular folder.
#   * Then check fit errors and compare with corresponding plots.
#   * Write a short report on this to Vale.

fit_errs = {}
failed_files = []
# Iterate through files.
for in_filename in os.listdir(PATH_SYNTHETIC):
    file = PATH_SYNTHETIC + '/' + in_filename
    df = pd.read_csv(file,sep="    ", engine="python", names=COL_LABELS)

    # Cut x to only include assumed relevant region.
    dist_min = df.loc[df["flux"].idxmin()]["wavelength"]
    df_tgt   = df[df["wavelength"].between(dist_min-10, dist_min+10)]
    x    = np.array(df_tgt["wavelength"])

    # Get y and yerr.
    y    = 1 - np.array(df_tgt["flux"])
    yerr = np.array(df_tgt["flux err"])

    # Normalize x.
    xmin = np.min(x)
    xmax = np.max(x)
    xn = (x - xmin) / (xmax - xmin) * 2 - 1

    # Plot data.
    plt.figure()
    plt.plot(xn, y, 'b-', label='1 - Normalized flux', alpha=0.4)
    plt.fill_between(xn, y - yerr/2, y + yerr/2, color='b', alpha=0.2)

    # Fit to Voigt.
    init_guess = [np.max(y), 0., .25, .25]
    try:
        popt, pcov = curve_fit(voigt, xn, y, p0=init_guess)
        fit_errs[in_filename] = np.sqrt(np.diag(pcov))
        # Plot fit.
        plt.plot(xn, voigt(xn, *popt), "r-", label="Voigt fit")
    except RuntimeError:
        fit_errs[in_filename] = "Fit error"
        failed_files.append(in_filename)

    # Plot data and fit.
    plt.title("File %s" % in_filename)
    plt.xlabel("norm. wavelength")
    plt.ylabel("1 - norm. flux")
    plt.legend()
    plt.savefig(PATH_PLOTS + '/' + in_filename + ".png")
    plt.close()

# Report errors.
print("Number of fit errors: %d" % len(failed_files))
print("Spectra that couldn't be fit:")
for failed_file in failed_files:
    print("  * " + failed_file)

# Plot fit errors.
val_map   = {0: "amp", 1: "center", 2: "sigma", 3: "gamma"}
list_errs = {
    "amp"    : [],
    "center" : [],
    "sigma"  : [],
    "gamma"  : []
}
n_failed_fits = 0
for fit_err in fit_errs.values():
    if isinstance(fit_err, str):
        n_failed_fits += 1
        continue
    for i, val in enumerate(fit_err):
        list_errs[val_map[i]].append(val)

for key, val in list_errs.items():
    counts, bins = np.histogram(val, bins=20)
    plt.stairs(counts, bins)

    plt.title("Voigt fit: " + key)
    plt.xlabel("Std. deviation")
    plt.ylabel("Count")

    plt.savefig(PATH_PLOTS + "/fit_stddev_" + key + ".png")
    plt.show()
