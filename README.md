# RR Lyrae temperature prediction
The purpose of this repository is to hold a set of tests and ML-based models to
predict the temperature of an RR Lyrae-class star based on the wings of its
Hydrogen lines (starting with Halpha at 656 nm).

## Motivation
Currently, the temperature of an RR Lyrae star at a snapshot of its phase
is obtained by
1. capturing a snapshot of its spectrum at a particular point in its
phase;
2. computing the synthetic spectrum at a given temperature; and
3. fitting the synthetic spectrum to the observed one to find a match of the
star's temperature.

While this methodology provides good results, it is quite slow: it takes about 5
minutes on an average computer. This is acceptable for small-scale datasets, but
we'll need to process very large ones in the future (> 1M stars). In addition,
a faster temperature prediction approach may allow us to later develop
predictions across the star's phase, improving the field of study of this class
of stars.

## Pending tasks
* [x] Define the input format.
* [ ] Get more input data.
* [x] Develop simple estimation models and see how well they behave.
* [ ] Estimate the sources of uncertainty and include them on the model.
    * [ ] Wing selection.
    * [ ] Uncertainty of the flux measurement.
    * [ ] Fit error.
* [ ] Develop a wing range selection algorithm.
* [ ] Play around with different spectrum/flux fitting functions (Chebyshev?).
* [ ] Play around with a model that can propagate uncertainties (Metropolis?).
* [ ] Look into the possibility of an ML-based de-noising approach. This would
broaden the range of the available input data to the noisier regions.

## Recommended reading
* [Wikipedia page on RR Lyrae](https://en.wikipedia.org/wiki/RR_Lyrae_variable).
