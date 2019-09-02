## <p align="center">Connectivity Circle Graph Creator Using the MNE Visualization Python Library</p>   
<p align="center"> Created by Damion V. Demeter</p>  
<p align="center"> at the Developmental Cognitive Neuroscience Lab (UT Austin)</p> 

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/3cdba526f9524e62b20e49e384d21afc)](https://app.codacy.com/app/iamdamion/MNE_circlegraph?utm_source=github.com&utm_medium=referral&utm_content=iamdamion/MNE_circlegraph&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/iamdamion/MNE_circlegraph.svg?branch=master)](https://travis-ci.org/iamdamion/MNE_circlegraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**"Insert matrix, receive circle graph!!"**  

This little script was originally created to use as an ultra flexible connectivity visualization tool...just add matrix! It will output a circle graph (with network color-coded and L/R hemisphere ordered labels) from any type of connectivity matrix supplied in .csv format. (Other applications will require code-tweaking...which is highly encouraged..just please let em' know I'm a neat guy who inspired you) ;)

Necessary items:  
- Connectivity matrix in .csv format. This can be a correlation matrix, "rank" matrix, etc, but must be UNdirected (currently...)  
- Network info .csv file. (An example is provided for the "UT 255" ROI set (Power 264 ROI set reduced because of missing scan coverage). This can be used as a template for any ROI set as long as the list matches the supplied matrix's dimensions)
 
### Prerequisites
This script requires the MNE visualization library for python. More info can be found here: https://martinos.org/mne/stable/index.html   
Sadly, this script still uses python 2.7, so the best way to install MNE that works with 2.7 is to pip install this version:
```
pip install mne==0.17.2
```
A quick python 3 update should be up when I get a few hours to throw it together. All other requirements should be commonly installed in any neuro-python env and any version should work (matplotlib, numpy, etc)   
**Note: This will output a .png file that you will need to crop. Currently, ROI text labels are turned off because they are visually cluttered, but smaller matrices/ROI sets could use them. However, this is hardcoded at this point. This will also be in the updated version as an argument, etc.**

Usage and Argument List:
```
usage: CIRCLE_GRAPH.py [-h] [-color COLOR] [-g GROUP_NAME [GROUP_NAME ...]]
                       [-i INFO_CSV] -mat MAT -o OUT_PATH
                       [-t THRESH_LIST [THRESH_LIST ...]] [-tdir TDIR]

Circle Maker: This script takes a matrix file made using an ROI info .csv (see
example file). It will make a hemisphere-split circle graph with functional
connections. One or multiple thresholds can be used. Thresholds can be
correlation values OR they can be any value (such as "rank" values if the
matrix is a CV fold count matrix, etc). Inputs and options will be expanded as
they come up. See -h for input options.Last Modified by Damion Demeter,
01.09.19

optional arguments:
  -h, --help            show this help message and exit
  -color COLOR          Color scheme type. l=light, d=dark. (Default=d)
  
  -g GROUP_NAME [GROUP_NAME ...]
                        Name to put as title on graph *AND* file name.
                        
  -i INFO_CSV           Path to ROI_SET_INFO.csv file. (Default=UT 255 ROI set)
  -mat MAT              Path to MATRIX.csv file. MUST be in .csv format.
  -o OUT_PATH           Path to output directory. All graph images (png) will be saved here.
  
  -t THRESH_LIST [THRESH_LIST ...]
                        SPACE separated list of threshold values. One graph
                        will be made per value. If blank, no threshold will be
                        applied. (Default = None) (default: [0])
  -tdir TDIR            Threshdold direction. "less"= less than thresh value.
                        "great" = greater than. (Default = "less")
```												
### Outputs:
By default, you will receive a .png file for each threshold you request in the output directory you specify. Please use group name argument if running for multiple groups or files will be overwritten.   
**It's suggested you re-name and move them from here, but whatever works for your personal workflow.**
	
