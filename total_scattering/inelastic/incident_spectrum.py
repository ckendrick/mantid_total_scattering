import numpy as np
from scipy import signal, ndimage, interpolate, optimize

from mantid import mtd
from mantid.simpleapi import \
    ConvertToPointData, \
    ConvertUnits, \
    CreateWorkspace, \
    LoadNexusMonitors, \
    Rebin, \
    ResampleX, \
    SplineSmoothing

# ----------------------------------------------------------------------------------------- #
# Functions for fitting the incident spectrum


def getFitRange(x, y, x_lo, x_hi):
    if x_lo is None:
        x_lo = min(x)
    if x_hi is None:
        x_hi = max(x)

    x_fit = x[(x >= x_lo) & (x <= x_hi)]
    y_fit = y[(x >= x_lo) & (x <= x_hi)]
    return x_fit, y_fit


def fitCubicSpline(x_fit, y_fit, x, s=1e15):
    tck = interpolate.splrep(x_fit, y_fit, s=s)
    fit = interpolate.splev(x, tck, der=0)
    fit_prime = interpolate.splev(x, tck, der=1)
    return fit, fit_prime


def fitCubicSplineViaMantidSplineSmoothing(InputWorkspace, Params, **kwargs):
    Rebin(
        InputWorkspace=InputWorkspace,
        OutputWorkspace='fit',
        Params=Params,
        PreserveEvents=True)
    SplineSmoothing(
        InputWorkspace='fit',
        OutputWorkspace='fit',
        OutputWorkspaceDeriv='fit_prime',
        DerivOrder=1,
        **kwargs)
    return mtd['fit'].readY(0), mtd['fit_prime_1'].readY(0)


def fitHowellsFunction(x_fit, y_fit, x):
    # Fit with analytical function from HowellsEtAl
    def calc_HowellsFunction(
            lambdas,
            phi_max,
            phi_epi,
            lam_t,
            lam_1,
            lam_2,
            a):
        term1 = phi_max * ((lam_t**4.) / lambdas**5.) * \
            np.exp(-(lam_t / lambdas)**2.)
        term2 = (phi_epi / (lambdas**(1. + 2. * a))) * \
            (1. / (1 + np.exp((lambdas - lam_1) / lam_2)))
        return term1 + term2

    def calc_HowellsFunction1stDerivative(
            lambdas, phi_max, phi_epi, lam_t, lam_1, lam_2, a):
        term1 = (((2 * lam_t**2) / lambdas**2) - 5.) * (1. / lambdas) * \
            phi_max * ((lam_t**4.) / lambdas**5.) * np.exp(-(lam_t / lambdas)**2.)
        term2 = ((1 + 2 * a) / lambdas) \
            * (1. / lambdas) * (phi_epi / (lambdas ** (1. + 2. * a))) \
            * (1. / (1 + np.exp((lambdas - lam_1) / lam_2)))
        return term1 + term2

    params = [1., 1., 1., 0., 1., 1.]
    params, convergence = optimize.curve_fit(
        calc_HowellsFunction, x_fit, y_fit, params)
    fit = calc_HowellsFunction(x, *params)
    fit_prime = calc_HowellsFunction1stDerivative(x, *params)
    return fit, fit_prime


def fitCubicSplineWithGaussConv(x_fit, y_fit, x, sigma=3):
    # Fit with Cubic Spline using a Gaussian Convolution to get weights
    def moving_average(y, sigma=sigma):
        b = signal.gaussian(39, sigma)
        average = ndimage.filters.convolve1d(y, b / b.sum())
        var = ndimage.filters.convolve1d(np.power(y - average, 2), b / b.sum())
        return average, var

    avg, var = moving_average(y_fit)
    spline_fit = interpolate.UnivariateSpline(
        x_fit, y_fit, w=1. / np.sqrt(var))
    spline_fit_prime = spline_fit.derivative()
    fit = spline_fit(x)
    fit_prime = spline_fit_prime(x)
    return fit, fit_prime


# ----------------------------------------------------------------------------------------- #
# Get incident spectrum from Monitor

def GetIncidentSpectrumFromMonitor(
        Filename,
        OutputWorkspace="IncidentWorkspace",
        IncidentIndex=0,
        TransmissionIndex=1,
        Binning=".1,6000,2.9",
        BinType="ResampleX"):

    # -------------------------------------------------
    # Joerg's read_bm.pro code

    # Loop workspaces to get each incident spectrum
    monitor = 'monitor'
    LoadNexusMonitors(Filename=Filename, OutputWorkspace=monitor)
    ConvertUnits(InputWorkspace=monitor, OutputWorkspace=monitor,
                 Target='Wavelength', EMode='Elastic')
    lambdaMin, lambdaBinning, lambdaMax = [
        float(x) for x in Binning.split(',')]
    for x in [lambdaMin, lambdaBinning, lambdaMax]:
        print(x, type(x))
    if BinType == 'ResampleX':
        ResampleX(InputWorkspace=monitor,
                  OutputWorkspace=monitor,
                  XMin=[lambdaMin],  # TODO change ResampleX
                  XMax=[lambdaMax],
                  NumberBins=abs(int(lambdaBinning)),
                  LogBinning=(int(lambdaBinning) < 0),
                  PreserveEvents=True)
    elif BinType == 'Rebin':
        Rebin(InputWorkspace=monitor,
              OutputWorkspace=monitor,
              Params=[lambdaMin, lambdaBinning, lambdaMax],
              PreserveEvents=True)
    ConvertToPointData(InputWorkspace=monitor, OutputWorkspace=monitor)

    lam = mtd[monitor].readX(IncidentIndex)    # wavelength in A
    bm = mtd[monitor].readY(IncidentIndex)     # neutron counts / microsecond
    # Pressure (empirically adjusted to match eff.)
    p = 0.000794807
    thickness = .1                        # 1 mm = .1 cm
    abs_xs_3He = 5333.0                   # barns for lambda == 1.798 A
    p_to_rho = 2.43e-5                    # pressure to rho (atoms/angstroms^3)
    # p is set to give efficiency of 1.03 10^-5 at 1.8 A
    e0 = abs_xs_3He * lam / 1.798 * p_to_rho * p * thickness
    print('Efficiency:', 1. - np.exp(-e0))
    bmeff = bm / (1. - np.exp(-e0))      # neutron counts / microsecond
    print(bmeff)
    # bmeff = bmeff / constants.micro      # neutron counts / second

    CreateWorkspace(DataX=lam, DataY=bmeff,
                    OutputWorkspace=OutputWorkspace, UnitX='Wavelength')
    mtd[OutputWorkspace].setYUnit('Counts')
    return mtd[OutputWorkspace]


def FitIncidentSpectrum(InputWorkspace, OutputWorkspace,
                        FitSpectrumWith='GaussConvCubicSpline',
                        BinningForFit="0.15,0.05,3.2",
                        BinningForCalc=None):

    incident_ws = mtd[InputWorkspace]

    # Fit Incident Spectrum
    # Get axis for actual calc (either provided in BinningForCalc or extracted
    # from incident wksp)
    incident_index = 0
    if BinningForCalc is None:
        x = incident_ws.readX(incident_index)
    else:
        try:
            params = [float(x) for x in BinningForCalc.split(',')]
        except AttributeError:
            params = [float(x) for x in BinningForCalc]
        xlo, binsize, xhi = params
        x = np.arange(xlo, xhi, binsize)

    Rebin(
        incident_ws,
        OutputWorkspace='fit',
        Params=BinningForFit,
        PreserveEvents=True)
    x_fit = np.array(mtd['fit'].readX(incident_index))
    y_fit = np.array(mtd['fit'].readY(incident_index))

    if FitSpectrumWith == 'CubicSpline':
        fit, fit_prime = fitCubicSpline(x_fit, y_fit, x, s=1e7)
    elif FitSpectrumWith == 'CubicSplineViaMantid':
        fit, fit_prime = fitCubicSplineViaMantidSplineSmoothing(
            InputWorkspace, Params=BinningForFit, MaxNumberOfBreaks=8)
    elif FitSpectrumWith == 'HowellsFunction':
        fit, fit_prime = fitHowellsFunction(x_fit, y_fit, x)
    elif FitSpectrumWith == 'GaussConvCubicSpline':
        fit, fit_prime = fitCubicSplineWithGaussConv(x_fit, y_fit, x, sigma=2)
    else:
        raise Exception("Unknown method for fitting incident spectrum")
        return

    CreateWorkspace(
        DataX=x,
        DataY=np.append(
            fit,
            fit_prime),
        OutputWorkspace=OutputWorkspace,
        UnitX='Wavelength',
        NSpec=2,
        Distribution=False)
    return mtd[OutputWorkspace]
