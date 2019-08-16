#!/usr/bin/env python
# See help option for usage
#
# Originally written by Damion Demeter 10.30.18
#
# Circle Graph Maker - Insert matrix, receive circle graph visualization!
# (see last revision's modified date)
from __future__ import division

import argparse, csv, os, re, sys
import numpy as np
from mne.viz import circular_layout, plot_connectivity_circle
import matplotlib.pyplot as plt

last_modified = 'Last Modified by Damion Demeter, 01.09.19'
here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
############
prog_descrip = 'Circle Maker: This script takes a matrix file made using an \
ROI info .csv (see example file). It will make a hemisphere-split circle graph\
with functional connections. One or multiple thresholds can be used.\
Thresholds can be correlation values OR they can be any value (such as "rank"\
values if the matrix is a CV fold count matrix, etc). Inputs and options will\
be expanded as they come up. See -h for input options.' + last_modified


def main(argv=sys.argv):
    arg_parser = argparse.ArgumentParser(description=prog_descrip,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Check for arguments. #
    if len(sys.argv[1:]) == 0:
        print '\nArguments required. Use -h option to print FULL usage.\n'
    arg_parser.add_argument('-color', metavar='COLOR', action='store', required=False, default='d',
                            help=('Color scheme type. l=light, d=dark. (Default=d)'),
                            dest='color_type'
                            )
    arg_parser.add_argument('-g', metavar='GROUP_NAME', nargs='+', action='store', required=False, default='',
                            help=('Name to put as title on graph *AND* file name. (Default=None)'),
                            dest='group_name'
                            )
    arg_parser.add_argument('-i', metavar='INFO_CSV', action='store', required=False, default='UT_255',
                            help=('Path to ROI_SET_INFO.csv file. (Default=UT 255 ROI set)'),
                            dest='info_csv'
                            )
    arg_parser.add_argument('-mat', metavar='MAT', action='store', required=True,
                            help=('Path to MATRIX.csv file. MUST be in .csv format.'),
                            dest='mat_path'
                            )
    arg_parser.add_argument('-o', metavar='OUT_PATH', action='store', required=True,
                            help=('Path to output directory. All graph images (png) will be saved here.'),
                            dest='out_path'
                            )
    arg_parser.add_argument('-t', action='store', nargs='+', type=str, required=False, default=[0],
                            help=('SPACE separated list of threshold values. One graph will be made per value. \
                            If blank, no threshold will be applied. (Default = None)'),
                            dest='thresh_list'
                            )
    arg_parser.add_argument('-tdir', action='store', required=False, default = 'less',
                            help=('Threshdold direction. "less"= less than thresh value. "great" = greater than. (Default = "less")'),
                            dest='tdir'
                            )
    args = arg_parser.parse_args()
    #################################################
    ## Script Argument Verification and Assignment ##
    #################################################
    print '\n--------------------- setup info ---------------------------------'
    ## CHECK COLOR TYPE ##
    if args.color_type == 'l':
        color_type = 'LIGHT'
    elif args.color_type == 'd':
        color_type = 'DARK'
    else:
        print 'Your color type choice is not valid. Check and re-run. Exiting...'
        sys.exit()
    ### FORMAT GROUP NAME for TITLE AND FILE NAME ###
    if len(args.group_name) > 0:
        title = ' '.join(args.group_name)
        file_name = '_'.join(args.group_name) + '_CIRCLE_GRAPH'
    else:
        title = ''
        file_name = 'CIRCLE_GRAPH'
    ### VERIFY INFO CSV PATH ###
    if args.info_csv == 'UT_255':
        info_path = os.path.join(here,'255_circle_graph_info.csv')
    else:
        info_path = args.info_csv
    if os.path.isfile(info_path):
        print '- Using info.csv file:  ' + os.path.basename(info_path)
    else:
        print 'Info .csv file path could NOT be verified and is required. Check and re-run. Exiting...'
        sys.exit()
    ### VERIFY MATRIX PATH ###
    if os.path.isfile(args.mat_path):
        mat_path = args.mat_path
        print '- Using matrix.csv file:\n  ' + mat_path
    else:
        print 'Matrix .csv file path could NOT be verified and is required. Check and re-run. Exiting...'
        sys.exit()
    ### CHECK THRESHOLD LIST ###
    if len(args.thresh_list) == 1 and args.thresh_list[0] == 0:
        print '- No threshold(s) supplied. Whole matrix will be used.'
    else:
        print '- The following threshold(s) will be applied:\n  '+ str(args.thresh_list)
        print '  All values *' + args.tdir + ' than* the threshold(s) will be ZEROED OUT.'
    ### VERIFY OUTPUT PATH EXISTS ###
    if os.path.isdir(args.out_path):
        out_path = args.out_path
        print '- All output files will be saved here:\n  ' + out_path
    else:
        print 'Output directory could NOT be verified and is required. Check and re-run. Exiting...'
        sys.exit()
    print '--------------------------- end ---------------------------------\n'
    #################################################
    ##          Global Variable Assignment         ##
    #################################################

    ## BUILD INFO CSV DICTIONARY ##
    info_dict = {}
    reader = csv.DictReader(open(info_path, 'rU'))
    for row in reader:
        info_dict[row['label']] = {'hemi': row['hemi'],
                                   'color': row['color'],
                                   'network': row['network'],
                                   'net_color': row['net_color']}

    #################################################
    ##                  FUNCTIONS                  ##
    #################################################
    def natural_sort(l):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)

    def load_thresh_mat(mat_path,thr):
        ## LOAD MATRIX .csv ##
        mat = np.genfromtxt(mat_path, delimiter=',')
        ## GET UNIQUE CONNECTIONS ##
        mat = np.tril(mat, -1)
        ## THRESHOLD MATRIX ##
        threshmat = mat.copy()
        threshmat[threshmat < thr] = 0

        return threshmat

    def make_circle(threshmat, outpath, label_names, thr):
        ## GET VMIN AND MAX FROM MATRIX
        # maxval = threshmat.max()
        # minval = np.min(threshmat[np.nonzero(threshmat)]) - 1
        maxval = None
        minval = None

        ## CHECK CIRCLE GRAPH COLOR TYPE ##
        if color_type == 'DARK':
            fc = 'black'
        elif color_type == 'LIGHT':
            fc = 'white'

        ## PREP FIGURE
        fig = plt.figure(num=None, figsize=(30, 30), facecolor=fc)

        ## MAKE NODES ANGLES ##
        node_angles = circular_layout(label_names, node_order, start_pos=sp, group_boundaries=split)

        ## REMOVE NAMES IF TRUE ##
        remove_names = True
        if remove_names == True:
            label_names = [''] * len(label_names)

        ## WRITE GRAPH TO FIG ##
        if color_type == 'DARK':
            plot_connectivity_circle(threshmat, label_names, node_angles=node_angles, node_colors=label_colors,
                                    title=title, fontsize_title=48, textcolor='white', facecolor='black',
                                    node_edgecolor='black', node_linewidth = .5, linewidth=1.5, fontsize_names=8,
                                    colormap='hot', vmin=minval, vmax=maxval, 

                                    ### make vmin and max the values from the min/max of matrix

                                    colorbar_size=0.2, colorbar_pos=(-1, .5), fontsize_colorbar=28, colorbar=True,
                                    padding=6.0, fig=fig, subplot=111, interactive=False, show=False)

            # ADD Left/Right Labels
            plt.gcf().text(.22, .5, 'L', color='white', fontsize=48)
            plt.gcf().text(.633, .5, 'R', color='white', fontsize=48)

        elif color_type == 'LIGHT':
            plot_connectivity_circle(threshmat, label_names, node_angles=node_angles, node_colors=label_colors,
                                    title=title, fontsize_title=48, textcolor='black', facecolor='white',
                                    node_edgecolor='black', node_linewidth = .5, linewidth=1.5, fontsize_names=8,
                                    colormap='hot_r', vmin=minval, vmax=maxval, # colormap='YlGnBu'

                                    ### make vmin and max the values from the min/max of matrix

                                    colorbar_size=0.2, colorbar_pos=(-1, .5), fontsize_colorbar=28, colorbar=True,
                                    padding=6.0, fig=fig, subplot=111, interactive=False, show=False)

            # ADD Left/Right Labels
            plt.gcf().text(.22, .5, 'L', color='black', fontsize=48)
            plt.gcf().text(.633, .5, 'R', color='black', fontsize=48)


        ## SAVE FIGURE ##
        out_fig = os.path.abspath(os.path.join(out_path,file_name + '_THR' + str(thr)))

        # have to re-set the facecolor before saving #
        fig.savefig(out_fig, facecolor=fc)



    #################################################
    ##               MAIN SCRIPT ENTRY             ##
    #################################################
    print '\nUsing the UT 255 ROI set and colors/names...'
    ## FIRST CREATE THE CORRECT LISTS FOR MNE FUNCTION ##
    # FULL LABEL NAMES LIST #
    label_names = natural_sort(info_dict.keys())

    ## MAKE NODE ORDER. REORDER THE ABOVE VALUES TO THE ORDER YOU WANT IN FINAL CIRCLE (must be ALL same values from label_names list) ##
    # HERE WE ARE SEPARATING BY HEMISPHERE #
    left_hemi = [ i for i in natural_sort(info_dict.keys()) if info_dict[i]['hemi'] == 'L' ]

    ## THE LIST GOES FROM TOP, COUNTER CLOCK-WISE. SO THE RIGHT HALF NEEDS TO BE IN REVERSE ORDER ##
    right_hemi_reversed = [ i for i in reversed(natural_sort(info_dict.keys())) if info_dict[i]['hemi'] == 'R' ]

    ## NOW CONTANTENATE INTO ONE LONG LIST - because MNE wants this ##
    node_order = left_hemi + right_hemi_reversed

    ## MAKE COLOR LIST ##
    # COLOR LIST GOES IN THE *ORIGINAL* ORDER (MATCHES LABEL NAMES LIST ORDER) #
    # COLORS ARE 3 VALUE TUPLES, IN DECIMAL, FOLLOWED BY OPACITY VAL. IF YOU HAVE RGB, DIVIDE THE RGB VALUE BY 255 #
    label_colors = [ tuple(map(float, info_dict[i]['color'].split(' '))) for i in natural_sort(info_dict.keys()) ]

    ## CHOOSE WHERE TO PUT THE SPLIT ##
    # FOR THE 255, this is the range of first ROI to the *COUNT* of the last ROI on the left side
    split = [0,124]
    # START POSITION. DEFAULT IS 90, WHICH IS TOP OF THE CIRCLE
    sp = 90

    # LOOP OVER THRESHOLDS AND LOAD MATRIX, THEN THRESHOLD MATRIX #
    for threshold in args.thresh_list:
        thr = int(threshold)
        print 'Applying threshold of ' + str(threshold)
        threshmat = load_thresh_mat(mat_path,thr)

        ## TAKE THRESHOLD MATRIX AND MAKE/SAVE CIRCLE GRAPH ##
        make_circle(threshmat,out_path,label_names,thr)


if __name__ == '__main__':
    sys.exit(main())