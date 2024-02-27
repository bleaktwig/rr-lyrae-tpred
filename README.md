# RR Lyrae temperature prediction
The purpose of this repository is to hold a set of tests and ML-based models to
predict the temperature of a RR Lyrae-class star based on the wings of its
Hydrogen spectrum.

## Motivation
Currently, the temperature of a RR Lyrae-class star at a snapshot of its phase
is obtained by
1. capturing a snapshot of its Hydrogen spectrum at a particular point of its
phase;
2. simulating its expected spectrum at a given temperature; and
3. fitting the simulated spectrum to the real one to find a match of the star's
temperature.

While this methodology provides good results, it is quite slow: it takes about 5
minutes on an average computer. This is acceptable for small scale datasets, but
we'll need to process very large ones in the future (> 1M stars). In addition,
a faster temperature prediction approach may allow us to later develop
predictions across the star's phase, improving the field of study of this class
of stars.

## Pending tasks
* [ ] Define the input format. So far, we know it should include the flux at a
sector of its discretized spectrum (the wings), and its signal-to-noise ratio.
* [ ] Get enough input data to train simple models.
* [ ] Develop simple estimation models and see how well they behave.
* [ ] Look into the possibility of an ML-based de-noising approach. This would
broaden the range of the available input data to the noisier regions.

## Recommended reading
* [Wikipedia page on RR Lyrae](https://en.wikipedia.org/wiki/RR_Lyrae_variable).
