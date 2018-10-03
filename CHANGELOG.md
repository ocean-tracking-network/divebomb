# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2018-08-01
### Added
- New sample data set included in docs
- New error message when sample size is too low

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
