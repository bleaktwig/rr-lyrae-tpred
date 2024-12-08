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

"""
Take a flux distribution dataframe and constrain the wavelength to assumed rele-
vant region. This reduces the fitting time by a large margin, as there are much
less points to fit against.
"""
def constrain_wavelength(df):
    dist_min = df.loc[df["flux"].idxmin()]["wavelength"]
    df_tgt   = df[df["wavelength"].between(dist_min-10, dist_min+10)]
    return df_tgt

"""Normalize wavelength distribution so that it spans from -1 to 1."""
def norm_wavelength(x):
    x_min, x_max = np.min(x), np.max(x)
    x_norm = (x - x_min) / (x_max - x_min) * 2 - 1
    return x_norm, x_min, x_max

"""Voigt function."""
def voigt(x, amp, center, sigma, gamma):
    return amp * voigt_profile(x - center, sigma, gamma)

"""Double Voigt function sharing the center."""
def voigt2(x, c, a1, a2, s1, s2, g1, g2):
    return voigt(x, a1, c, s1, g1) + voigt(x, a2, c, s2, g2)

# --+ Code +--------------------------------------------------------------------
"""Double Voigt function sharing the center."""
def voigt2_t(x, c, a1, a2, s1, s2, g1, g2):
    return a1 * voigt_profile(x - c, s1, g1) + a2 * voigt_profile(x - c, s2, g2)

# Fit one random file and show plot.
in_filename = random.choice(os.listdir(PATH_SYNTHETIC))
file = PATH_SYNTHETIC + '/' + in_filename
df = pd.read_csv(file, sep="    ", engine="python", names=COL_LABELS)

# Get x, y, and yerr.
df_tgt = constrain_wavelength(df)
x = np.array(df_tgt["wavelength"])
y = 1 - np.array(df_tgt["flux"])
yerr = np.array(df_tgt["flux err"])

# Plot data.
plt.figure()
plt.plot(x, y, 'b-', label='1 - Normalized flux', alpha=0.4)
plt.fill_between(x, y - yerr/2, y + yerr/2, color='b', alpha=0.2)

# Get initial guess and bounds to help the fit.
center = df.loc[df["flux"].idxmin()]["wavelength"]
#             c         a1             a2             s1      s2      g1      g2
init_guess = [center,   2*np.max(y)/3, 1*np.max(y)/3, 3.,     0.,     3.,     20.]
bounds_l   = [center-1, 0.,            1*np.max(y)/3, 0.,     0.,     0.,      0.]
bounds_u   = [center+1, np.inf,        np.max(y)/2,   np.inf, np.inf, np.inf, np.inf]

# Fit to Voigt(s).
popt, pcov = curve_fit(voigt2_t, x, y, p0 = init_guess, bounds = (bounds_l, bounds_u))
c, a1, a2, s1, s2, g1, g2 = popt
param_names = ["c  = ", "a1 = ", "a2 = ", "s1 = ", "s2 = ", "g1 = ", "g2 = "]
for i, param in enumerate(popt):
    print("%s%f" % (param_names[i], param))

# Plot fit(s).
plt.plot(x, voigt(x, a1, c, s1, g1), "#2B6581", label="Voigt 1")
plt.plot(x, voigt(x, a2, c, s2, g2), "#257263", label="Voigt 2")
plt.plot(x, voigt2_t(x, *popt),      "#623B86", label="Sum")

# Include plot details and show.
plt.title("File %s" % in_filename)
plt.xlabel("norm. wavelength")
plt.ylabel("1 - norm. flux")
plt.legend()
plt.show()

# Fit all input files. Fit error of each file is save to `fit_errs` (key is file
#     name), failed fits are stored in `failed_files`. For each successful fit,
#     a plot is saved in `./plots`.
fit_errs = {}
failed_files = []
# Iterate through files.
for in_filename in os.listdir(PATH_SYNTHETIC):
    file = PATH_SYNTHETIC + '/' + in_filename
    df = pd.read_csv(file,sep="    ", engine="python", names=COL_LABELS)

    # Get x, y, and yerr.
    df_tgt = constrain_wavelength(df)
    xn, xmin, xmax = norm_wavelength(np.array(df_tgt["wavelength"]))
    y    = 1 - np.array(df_tgt["flux"])
    yerr = np.array(df_tgt["flux err"])

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

    # Plot and fit.
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
    plt.hist(val, bins=20)

    plt.title("Voigt fit: " + key)
    plt.xlabel("Std. deviation")
    plt.yscale("log")
    plt.ylabel("Count")

    plt.savefig(PATH_PLOTS + "/fit_stddev_" + key + ".png")
    plt.show()
