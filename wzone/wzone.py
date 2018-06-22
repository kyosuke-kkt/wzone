
# python 2.7 default packages
import os
import cPickle as pickle
import datetime
import calendar
import itertools
import pkg_resources

# non-default packages
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn import preprocessing

import gzip_pickle

# convert date string to numeric
def numftime(d, format = '%Y-%m-%d'):

    """A function that converts a date string to a timestamp integer."""

    timestamp = calendar.timegm(datetime.datetime.strptime(d, format).timetuple())

    return timestamp

# check data types
def format(data, dtype, make_list = True):

    """A function that transform dates to integers."""

    # if d is not none
    if data is not None:

        # if d belongs to a specified type, make it as a list
        if not np.issubsctype(type(data), list):
            data = [data]

        # if data is not dtype or a list, return error
        if not np.issubsctype(type(data), list):
            TypeError('data must be ' + str(type(dtype).__name__) + ' or its list.')

        # format
        data = [dtype(d) for d in data]

        # finally unlist if make_list is False
        if (not make_list) & len(data) == 1:
            data = data[0]

    return data

# write ESRI ASCII file
def write_asc(array, out_path, ncols, nrows, xllcenter, yllcenter, cellsize, nodata_value = -999, fmt = '%i'):

    # delete a file if it exists
    if os.path.exists(out_path):
        os.remove(out_path)

    # write the matrix as a esri ascii file
    txt_header = 'ncols ' + str(ncols) + '\n' + \
                 'nrows ' + str(nrows) + '\n' + \
                 'xllcenter ' + str(xllcenter) + '\n' + \
                 'yllcenter ' + str(yllcenter) + '\n' + \
                 'cellsize ' + str(cellsize) + '\n' + \
                 'nodata_value ' + str(nodata_value) + '\n'
    np.savetxt(out_path, array, fmt=fmt, delimiter=' ', header=txt_header, comments='')

# make a prediction based on the outcome of ensemble_osvm
def osvm_ensemble(osvm_list, mat, cut = 0.5):

    """
    A function that ensembles predictions of multiple OC-SVM models (intended for internal use).
    :param osvm_list: A list of precompiled sklearn.svm.OneClassSVM classes. For details of svm.OneClassSVM refer
                      to sklearn documentation.
    :param mat: A 2-dimensional numpy array (row: observations, column: variables).
    :param cut: A float between 0.0 and 1.0. If equal or more than this proportion of models make positive predictions,
                the ensemble prediction is positive.

    :return: A list of predicted values (1 for positive and 0 for negative prediction).
    """

    # create a list that saves the predictions
    pred_list = []

    # if not an instance of a list
    if not isinstance(osvm_list, list):
        osvm_list = [osvm_list]

    # loop for each estimator
    for osvm in osvm_list:

        # make a prediction
        pred_tmp = osvm.predict(mat)

        # change to 0 and 1
        pred_tmp = (np.array(pred_tmp) + 1) / 2

        # append
        pred_list.append(pred_tmp)

    # majority votes
    if len(pred_list) > 1:
        votes = list(sum(map(np.array, pred_list)))
        out = 1*np.array([v >= cut*float(len(osvm_list)) for v in votes])
    else:
        out = pred_list[0]

    # return
    return out

# GED ID query
def find_ids(country = None, country_id = None, date_from = None, date_to = None, type_of_violence = None,
             min_nobs = None, estimated_only = True):

    """
    A function for querying the UCDPGED conflict IDs.
    :param country: A string or a list of strings of country names. The country names must be consistent with those
                    in the UCDPGED. If specified, it returns conflict IDs that occurred in the countries.
    :param country_id: An integer or a list of integers of country IDs. The country IDs must be consistent with those
                       in the UCDPGED. If specified, it returns conflict IDs that occurred in the corresponding
                       countries.
    :param date_from: A string of a date in the format of YYYY-MM-DD (eg. 2000-01-01).
                      If specified, it returns conflict IDs whose last conflict event occurred after
                      the specified date.
    :param date_to: A string of a date in the format of YYYY-MM-DD (eg. 2001-01-01).
                    If specified, it returns conflict IDs whose first conflict event occurred before
                    the specified date.
    :param type_of_violence: An integer or a list of integers of violence types. 1: state-based conflict, 2: non-state
                             conflict, 3: non-state conflict. For details of these classifications, refer to UCDPGED.
                             If specified, it returns conflict IDs relevant to the corresponding violence types.
    :param min_nobs: An integer of the minimum number of conflict events. If specified, it returns conflict IDs whose
                     numbers of conflict events are equal or more than the specified number.
    :param estimated_only: Logical. If True, it omits conflict IDs that have too few numbers of conflict events
                          (less than 10). For those conflict IDs, the OC-SVMs were not estimated and hence
                          gen_wzones function will not return any war zones.

    :return: A list of conflict IDs.
    """

    # load ged summary table
    ged_summary_path = pkg_resources.resource_filename('wzone', 'data/ged_summary.pkl')
    with open(ged_summary_path, 'rb') as f:
        ged_sum_df = pickle.load(f)

    # check and format data types
    country = format(country, str)
    country_id = format(country_id, int)
    date_from = format(date_from, str, make_list=False)
    date_to = format(date_to, str, make_list=False)
    type_of_violence = format(type_of_violence, int)
    min_nobs = format(min_nobs, int, make_list=False)

    # drop non-estimated
    if estimated_only:
        ged_sum_df = ged_sum_df.loc[ged_sum_df['n'] >= 10,:]

    # select by country
    if country is not None:
        reg_tmp = '|'.join(country)
        ged_sum_df = ged_sum_df.loc[ged_sum_df['country'].str.contains(reg_tmp),:]

    # select by country id
    if country_id is not None:
        reg_tmp = '|'.join([str(c) for c in country_id])
        ged_sum_df = ged_sum_df.loc[ged_sum_df['country_id'].str.contains(reg_tmp),:]

    # select by the first date of events (the final events happened before the specified date)
    if date_from is not None:
        ged_sum_df['date_end'] = pd.to_datetime(ged_sum_df['date_end'])
        ged_sum_df = ged_sum_df.loc[ged_sum_df['date_end'] >= datetime.datetime.strptime(date_from, '%Y-%m-%d'),:]

    # select by the last date of events (the first events happened after the specified date)
    if date_to is not None:
        ged_sum_df['date_start'] = pd.to_datetime(ged_sum_df['date_start'])
        ged_sum_df = ged_sum_df.loc[ged_sum_df['date_start'] <= datetime.datetime.strptime(date_to, '%Y-%m-%d'),:]

    # select by violence type
    if type_of_violence is not None:
        ged_sum_df = ged_sum_df.loc[ged_sum_df['type_of_violence'].isin(type_of_violence),:]

    # select by the minimum number of observations
    if min_nobs is not None:
        ged_sum_df = ged_sum_df.loc[ged_sum_df['n'] >= min_nobs,:]

    # return the remaining ids as a list
    out_ids = ged_sum_df['id'].tolist()
    if len(out_ids) == 0:
        Warning('There is no conflict IDs that meet your query.')
        return None
    else:
        return out_ids

# check tuned parameter values
def check_params(ids, with_date = True):

    """
    A function for querying the hyper-parameter values for given conflict IDs.
    :param ids: An integer or a list of integers of the UCDPGED conflict IDs. The conflict IDs must be consistent with
        those in the UCDPGED.
    :param with_date: Logical. If True, it returns parameter values for a model with date information.
        If False, it returns parameters values for a model without date information.

    :return: A list of lists in the form ``[[nu, gamma for the 1st ID], [nu, gamma for the 2nd ID], ...])``.
    """

    # load ged summary table
    if with_date:
        ged_param_path = pkg_resources.resource_filename('wzone', 'data/w_date/ged_optimal_parameters.pkl')
    else:
        ged_param_path = pkg_resources.resource_filename('wzone', 'data/wo_date/ged_optimal_parameters.pkl')
    with open(ged_param_path, 'rb') as f:
        ged_param_df = pickle.load(f)

    # check and format the ids input
    ids = format(ids, int)

    # check with_date
    if not isinstance(with_date, bool):
        TypeError('with_date must be a boolean.')

    # check if all IDs are valid
    valid_ids = [i for i in ids if i in ged_param_df['id'].tolist()]
    if len(valid_ids) == 0:
        ValueError('Any of the specified IDs is in the UCDPGED.')
    if len(valid_ids) < len(ids):
        Warning('Some of the specified IDs do not exist in the UCDPGED. They are dropped: ' + \
                ', '.join([i for i in ids if i not in valid_ids]) + '.')
        ids = valid_ids

    # select by the id
    ged_param_df = ged_param_df.loc[ged_param_df['id'].isin(ids), :]

    # return the remaining ids as a list
    out_params = ged_param_df[['nu', 'gamma']].values.tolist()
    return out_params

# find the first and last dates
def find_dates(ids, interval = None):

    """
    A function for querying relevant ranges of dates for given conflict IDs.
    :param ids: An integer or a list of integers of the UCDPGED conflict IDs. The conflict IDs must be consistent with
                those in the UCDPGED.
    :param interval: Either 'day', 'week', 'month', 'quarter', or 'year'. If not specified, it returns a list of
                     the first and last dates of conflict events for each conflict ID. If specified,
                     it returns a sequence of dates from the first to the last date for each conflict ID
                     at a given frequency.

    :return: A list of lists in the form ``[[date strings for the 1st ID], [date strings for the 2nd ID], ...])``.
    """

    # load ged summary table
    ged_summary_path = pkg_resources.resource_filename('wzone', 'data/ged_summary.pkl')
    with open(ged_summary_path, 'rb') as f:
        ged_sum_df = pickle.load(f)

    # check and format the ids input
    ids = format(ids, int)

    # check the format of interval
    if isinstance(interval, (type(None), str)):
        TypeError('interval must be None or a string.')
    if interval not in ['day', 'week', 'month', 'quarter', 'year']:
        ValueError("interval must be either 'day', 'week', 'month', 'quarter', or 'year'")

    # get a array of first and last dates
    date_list = ged_sum_df.loc[ged_sum_df['id'].isin(ids), ['date_start', 'date_end']].values.tolist()

    # make an output list
    out_list = []
    freq_dict = {'day': '1D', 'week': '1W', 'month': '1MS', 'quarter': '1QS', 'year': '1AS'}

    # if interval is not specified
    if interval is None:
        out_list = date_list

    # if interval is specified, convert it to the pd names
    elif interval in freq_dict.keys():

        # get the frequency
        freq = freq_dict[interval]

        for ds in date_list:

            # make a daily sequence
            dseq = pd.date_range(ds[0], ds[1], freq=freq)
            dseq = dseq.union([dseq[0] - 1, dseq[-1] + 1])
            dseq = [d.strftime('%Y-%m-%d') for d in dseq]
            out_list.append(dseq)

    # if invalid interval
    else:
        ValueError('The specified interval is not supported. Use day, week, month, quarter, or year.')

    # return
    return out_list

# wrapper for making a raster given conflict id and date
def gen_wzones(dates, ids, out_dir, save_novalue_raster = False, ensemble = False, cut = 0.5):

    """
    A function for creating conflict zones for given dates and conflict IDs.
    :param dates: A string or a list of strings of dates in the format of YYYY-MM-DD (eg. 2000-01-01).
        It also accepts None to generate time-invariant conflict zones.
    :param ids: An integer or a list of integers of the UCDPGED conflict IDs. The conflict IDs must be consistent with
        those in the UCDPGED.
    :param out_dir: A string of a path to an output folder. Conflict zones are saved in the specified directory
        as the ESRI ASCII raster format.
    :param save_novalue_raster: Logical. If False, no raster outputs are saved when there is no conflict zone.
        If True, zero-valued raster files (3600-by-1800) are created and saved when there is no conflict zone.
        Use this option sparingly as the zero-valued raster files are large and slow down the process.
    :param ensemble: Logical. If True, it uses bootstrapping ensemble. The ensemble slows down the data generation.
        Recommended only if cut is not 0.5.
    :param cut: A float between 0.0 and 1.0. Valid only when ensemble = True. If equal or more than this proportion
        of bootstrapped models make positive predictions, the location is considered as a part of a war zone.
        cut = 0.025 gives the 95% lower bootstrapping bound of war zone estimates. cut = 0.975 gives the 95%
        upper bootstrapping bound of war zone estimates.

    :return: A list of paths at which the output ESRI ASCII raster files are saved.
        The output file names are in a format of '[ConflictID]_[Date].asc'.
        An output raster has a spatial resolution of 0.1 degree (approximately 11 kilometers).
        Cell value 1 indicates a conflict zone, and the rest of the areas are non-conflict zones.
    """

    ####################################################################################################################
    ### error checks

    # check and format inputs
    dates = format(dates, str)
    ids = format(ids, int)
    cut = format(cut, float, make_list=False)

    # check out_dir
    if not isinstance(out_dir, str):
        TypeError('out_dir must be a string.')
    if not os.path.exists(out_dir):
        ValueError('out_dir does not exist.')

    # check boolean arguments
    if not isinstance(save_novalue_raster, bool):
        TypeError('save_novalue_raster must be a boolean.')
    if not isinstance(ensemble, bool):
        TypeError('ensemble must be a boolean.')


    # check cut
    if cut >= float(1):
        ValueError('cut must be less than 1.')
    if cut <= 0:
        ValueError('cut must be larger than 0.')

    # specify the data directory
    if dates is not None:
        data_dir = 'data/w_date/'
    else:
        data_dir = 'data/wo_date/'
        dates = [dates]

    # load scaler
    scaler_path = pkg_resources.resource_filename('wzone', data_dir + 'ged_scaler.pkl')
    with open(scaler_path, 'rb') as f:
        scaler_dict = pickle.load(f)

    # load a dictionary of estimates if ensemble
    if ensemble:
        osvm_est_path = pkg_resources.resource_filename('wzone', data_dir + 'ged_osvm_dict.gzip')
        osvm_est_dict = gzip_pickle.load(osvm_est_path)

    # load a light version
    else:
        osvm_est_path = pkg_resources.resource_filename('wzone', data_dir + 'ged_osvm_dict_light.pkl')
        with open(osvm_est_path, 'rb') as f:
            osvm_est_dict = pickle.load(f)

    # load ged summary table
    ged_summary_path = pkg_resources.resource_filename('wzone', 'data/ged_summary.pkl')
    with open(ged_summary_path, 'rb') as f:
        ged_sum_df = pickle.load(f)

    # check whether the IDs are valid
    valid_ids = [i for i in ids if i in list(osvm_est_dict.keys())]
    if len(valid_ids) == 0:
        ValueError('Any of the specified IDs is in the UCDPGED.')
    elif len(valid_ids) < len(ids):
        Warning('Some of the specified IDs do not exist in the UCDPGED. They are dropped: ' + \
                ', '.join([i for i in ids if i not in valid_ids]) + '.')
        ids = valid_ids

    # check whether there exist estimated models for the specified IDs
    estimated_ids = [i for i in valid_ids if osvm_est_dict[i] is not None]
    if len(estimated_ids) == 0:
        ValueError('No zone output for any IDs you specified due to their small samples (n<10).')
    elif len(estimated_ids) < len(ids):
        Warning('No zone output for some of the specified IDs due to their small samples (n<10). They are dropped: ' + \
                    ', '.join([i for i in ids if i not in estimated_ids]) + '.')
        ids = estimated_ids

    ####################################################################################################################
    ### prediction

    # create a coarse resolution mesh
    resf = 0.1
    resc = 1.0
    longc = np.arange(-180, 180, resc)
    latc = np.arange(-90, 90, resc)[::-1]
    matc = np.array(list(itertools.product(longc, latc)))

    # loop for each id
    txt_files = []
    for uid in ids:

        # to be sure, id is int
        uid_int = int(uid)

        # get scaler
        scaler_tmp = scaler_dict[uid_int]

        # extract the estimate for the specified violence episode
        est_tmp = osvm_est_dict[uid_int]

        # get the first and last event dates
        first_date = ged_sum_df.loc[ged_sum_df['id'] == uid_int, ['date_start']].values[0][0]
        last_date = ged_sum_df.loc[ged_sum_df['id'] == uid_int, ['date_start']].values[0][0]

        # loop for each day
        for date in dates:

            # if dates are specified
            if date is not None:

                # if date is not within a plausible range, warnings
                if numftime(date) < numftime(first_date):
                    Warning(str(uid) + ': ' + \
                            str(date) + ' is earlier than the date of the first event (' + str(first_date) + ').')
                elif numftime(date) > numftime(last_date):
                    Warning(str(uid) + ': ' + \
                            str(date) + ' is later than the date of the last event (' + str(first_date) + ').')

                # add the date to df
                matc_tmp = np.column_stack((matc, np.full((matc.shape[0], 1), numftime(date), int)))

            # if no date, no need to add date variable
            else:
                matc_tmp = matc.copy()

            # scale the df
            matc_scaled_tmp = scaler_tmp.transform(matc_tmp)

            # prediction at a coarse level
            predc_tmp = osvm_ensemble(est_tmp[0], matc_scaled_tmp, cut=cut)
            idxc_tmp = np.where(predc_tmp == 1)[0]

            # specify the output path
            txt_path = out_dir + '/' + str(uid) + '_' + str(date) + '.asc'

            # if there is at least one y=1
            if len(idxc_tmp) > 0:

                # get the spatial extent of possible positive cases
                min_tmp = matc_tmp[idxc_tmp, 0:2].min(axis = 0) - 3*resc
                max_tmp = matc_tmp[idxc_tmp, 0:2].max(axis = 0) + 3*resc

                # create a high-resolution matrix
                longf_tmp = np.arange(min_tmp[0], max_tmp[0], resf)
                latf_tmp = np.arange(min_tmp[1], max_tmp[1], resf)[::-1]
                matf_tmp = np.array(list(itertools.product(longf_tmp, latf_tmp)))

                # add date if date is specified
                if date is not None:
                    matf_tmp = np.column_stack((matf_tmp, np.full((matf_tmp.shape[0], 1), numftime(date), int)))

                # scale the data
                matf_scaled_tmp = scaler_tmp.transform(matf_tmp)

                # make a prediction at a finer level
                predf_tmp = osvm_ensemble(est_tmp, matf_scaled_tmp, cut=cut)

                # make a matrix of the predicted values
                ncols_tmp = len(longf_tmp)
                nrows_tmp = len(latf_tmp)
                pred_mat = np.reshape(predf_tmp, (int(nrows_tmp), int(ncols_tmp)), order='F')

                # write an ascii file
                write_asc(pred_mat, txt_path,
                          ncols = ncols_tmp,
                          nrows = nrows_tmp,
                          xllcenter = min_tmp[0],
                          yllcenter = min_tmp[1],
                          cellsize = resf)
                txt_files.append(txt_path)

            # if there is no positive prediction
            else:

                # if save no value raster
                if save_novalue_raster:

                    # zero matrix
                    pred_mat = np.zeros((int(180*resf), int(360*resf)), order='F', dtype=int)

                    # save it
                    write_asc(pred_mat, txt_path,
                              ncols = 360 / resf,
                              nrows = 180/ resf,
                              xllcenter = -180,
                              yllcenter = -90,
                              cellsize = resf)
                    txt_files.append(txt_path)

    # return the list of file paths
    return txt_files



