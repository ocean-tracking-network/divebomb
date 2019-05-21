# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2019-03-11
### Fixed
- Fixed issue with correcting dives offset function

## [1.0.5] - 2019-03-11
### Changed
- Changed the descent start cutoff and padding to only apply to 10s sample rates or higher
- Descent padding is limited to 1 step backwards instead of 2

### Fixed
- Fixed issue with ascent velocity including surface values as the minimum depth

## [1.0.4] - 2019-03-07
### Fixed
- Fixed bug in bottom peak count

## [1.0.3] - 2019-02-27
### Fixed
- Fixed bug handling gaps in time in data at the beginning of the dataset

## [1.0.2] - 2018-11-05
### Added
- Some dives are now marked as insufficient if they can't be properly profiles
- New sample data set included in docs
- New error message when sample size is too low for clustering

### Changed
- The starting point of the dive is now the first value that drop below the surface for surfacing animals
- ipython_display_mode catches and shows which dives have insufficient data


## [1.0.0] - 2018-08-01
### Added
- DeepDive class for handling non-durfacing animals
- Plotting function for non-surfacing animals
- Surface threshold argument for surfacing animals
- At depth argument for all animals
- Dive sensitivity argument for peak detection
- Minimal time between dives for peak detection

### Changed
- Detection method for determining dive starts is no based on peak detection
- Principle Component Analysis is run on all attributes, except ``dive_start``, ``dive_end``, and ``surface_threshold``
