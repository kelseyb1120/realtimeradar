#Working with a single file
import pyart
import os
import sys
from glob import glob
import platform
import copy
import netCDF4
import datetime
import numpy as np
from matplotlib import pyplot as plt
from boto.s3.connection import S3Connection
import boto3
import tempfile
import imp

lib_loc = os.path.join(os.path.expanduser('~'), 'unfunded_projects/realtimeradar/code/processing_code.py')
radar_codes = imp.load_source('radar_codes', lib_loc)

if __name__ == '__main__':
    station = 'KAMX'
    my_datetime = datetime.datetime.utcnow()
    radar = radar_codes.get_radar_from_aws(station, my_datetime)

    kdp_top = 10000.
    coh_pwr = copy.deepcopy(radar.fields['differential_phase'])
    coh_pwr['data'] = coh_pwr['data']*0.+1.
    radar.fields['NCP'] = coh_pwr
    phidp,kdp = pyart.correct.phase_proc_lp(radar,0.0,
                                          refl_field='reflectivity',
                                          LP_solver='cylp',
                                          ncp_field='NCP',
                                          rhv_field='cross_correlation_ratio',
                                          phidp_field='differential_phase',
                                          fzl = kdp_top,
                                          coef=.87,
                                          low_z=25., debug=True)
    radar.fields['cylp_processed_phase'] = phidp
    radar.fields['specific_differential_phase'] = kdp

    radar_codes.save_latest_kamx_z_png_s3(radar)
    radar_codes.save_latest_kamx_kdp_png_s3(radar)
    radar_codes.save_latest_kamx_zdr_png_s3(radar)
    radar_codes.save_latest_kamx_vr_png_s3(radar)


