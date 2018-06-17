
# python 2.7 default packages
import os
import pickle
import datetime
import calendar
import itertools
import pkg_resources

# non-default packages
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn import preprocessing

# convert date string to numeric
def numftime(d, format = '%Y-%m-%d'):

    """A function that converts a date string to a timestamp integer."""

    timestamp = calendar.timegm(datetime.datetime.strptime(d, format).timetuple())

    return timestamp

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
    :param date_from: A string of dates in the format of YYYY-MM-DD (eg. 2000-01-01).
                      If specified, it returns conflict IDs whose last conflict event occurred after
                      the specified date.
    :param date_to: A string of dates in the format of YYYY-MM-DD (eg. 2001-01-01).
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

    # check types
    if country is not None:
        if country is not list:
            country = [country]
        if not all([isinstance(c, str) for c in country]):
            ValueError('all elements in country must be string.')

    if country_id is not None:
        if country_id is not list:
            country_id = [country_id]
        if not all([isinstance(c, int) for c in country_id]):
            ValueError('all elements in country_id must be int.')

    if date_from is not None:
        if not isinstance(date_from, str):
            ValueError('date_from must be a string.')

    if date_to is not None:
        if not isinstance(date_to, str):
            ValueError('date_to must be a string.')

    if type_of_violence is not None:
        if type_of_violence is not list:
            type_of_violence = [type_of_violence]
        if not all([isinstance(v, int) for v in type_of_violence]):
            ValueError('all elements in violence_type must be int.')

    if min_nobs is not None:
        if min_nobs is not int:
            ValueError('min_nobs must be int.')

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
def check_params(ids):

        """
        A function for querying the hyper-parameter values for given conflict IDs.
        :param ids: An integer or a list of integers of the UCDPGED conflict IDs. The conflict IDs must be consistent with
                    those in the UCDPGED.

        :return: A list of lists in the form ``[[nu, gamma for the 1st ID], [nu, gamma for the 2nd ID], ...])``.
        """

        # load ged summary table
        ged_param_path = pkg_resources.resource_filename('wzone', 'data/ged_optimal_parameters.pkl')
        with open(ged_param_path, 'rb') as f:
            ged_param_df = pickle.load(f)

        # check the ids input
        if isinstance(ids, int):
            ids = [ids]
        if isinstance(ids, list):
            if not all([isinstance(i, int) for i in ids]):
                ValueError('all elements in ids must be int.')
        else:
            TypeError('ids must be a string, int, or list.')

        # check if all IDs are valid
        valid_ids = [i for i in ids if i in ged_param_df['id'].tolist()]
        if len(valid_ids) == 0:
            ValueError('Any of the specified IDs is in the UCDPGED.')
        if len(valid_ids) < len(ids):
            Warning('Some of the specified IDs do not exist in the UCDPGED. They are dropped: ' + \
                    ', '.join([i for i in ids if i not in valid_ids]) + '.')
            ids = valid_ids

        # select by the id
        ged_param_df = ged_param_df.loc[ged_param_df['id'] in ids, :]

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

    # check the ids input
    if isinstance(ids, int):
        ids = [ids]
    if isinstance(ids, list):
        if not all([isinstance(i, int) for i in ids]):
            ValueError('all elements in ids must be int.')
    else:
        TypeError('ids must be a string, int, or list.')

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
def gen_wzones(dates, ids, out_dir, res = 0.2, ensemble = False, cut = 0.5):

    """
    A function for creating conflict zones for given dates and conflict IDs.
    :param dates: A string or a list of strings of dates in the format of YYYY-MM-DD (eg. 2000-01-01).
    :param ids: An integer or a list of integers of the UCDPGED conflict IDs. The conflict IDs must be consistent with
                those in the UCDPGED.
    :param out_dir: A string of a path to an output folder. Conflict zones are saved in the specified directory
                    as the ESRI ASCII raster format.
    :param res: A float that specifies the spatial resolution of the output rasters. While a smaller values produces
                more precise zones, it also substantially slow downs the data generation. For a large amount of data,
                0.5 or 1 is recommended. For a relatively small amount of data, 0.1 is recommended.
    :param ensemble: Logical. If True, it uses bootstrapping ensemble. The ensemble slows down the data generation.
                     Recommended only if cut is not 0.5.
    :param cut: A float between 0.0 and 1.0. Valid only when ensemble = True. If equal or more than this proportion
                of bootstrapped models make positive predictions, the location is considered as a part of a war zone.
                cut = 0.025 gives the 95% lower bootstrapping bound of war zone estimates. cut = 0.975 gives the 95%
                upper bootstrapping bound of war zone estimates.

    :return: A list of paths to the output ESRI ASCII raster files.
    """

    ####################################################################################################################
    ### error checks

    # check the dates input
    if isinstance(dates, str):
        dates = [dates]
    if isinstance(dates, list):
        if not all([isinstance(d, str) for d in dates]):
            ValueError('all elements in dates must be string.')
    else:
        TypeError('dates must be a string or list.')

    # check the ids input
    if isinstance(ids, int):
        ids = [ids]
    if isinstance(ids, list):
        if not all([isinstance(i, int) for i in ids]):
            ValueError('all elements in ids must be string or int.')
    else:
        TypeError('ids must be a string, int, or list.')

    # check cut
    if cut >= float(1):
        ValueError('cut must be less than 1.')
    if cut <= 0:
        ValueError('cut must be larger than 0.')

    # load scaler
    scaler_path = pkg_resources.resource_filename('wzone', 'data/ged_scaler.pkl')
    with open(scaler_path, 'rb') as f:
        scaler_dict = pickle.load(f)

    # load estimates
    osvm_est_path = pkg_resources.resource_filename('wzone', 'data/ged_estimated_osvm.pkl')
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

    # create a mesh df
    long_tmp = np.arange(-180, 180, res)
    lat_tmp = np.arange(-90, 90, res)[::-1]
    df = pd.DataFrame(list(itertools.product(long_tmp, lat_tmp)), columns=['long', 'lat'])

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

            # temporary df
            df_tmp = df.copy()

            # if date is not within a plausible range return
            if numftime(date) < numftime(first_date):
                Warning(str(uid) + ': ' + \
                        str(date) + ' is earlier than the date of the first event (' + str(first_date) + ').')
            elif numftime(date) > numftime(last_date):
                Warning(str(uid) + ': ' + \
                        str(date) + ' is later than the date of the last event (' + str(first_date) + ').')

            # add the date to df
            df_tmp['date'] = numftime(date)

            # scale the df
            mat_tmp = scaler_tmp.transform(df_tmp.values)

            # if not ensemble
            if (not ensemble) & isinstance(est_tmp, list):
                est_tmp = est_tmp[0]

            # episode-specific prediction
            pred_tmp = osvm_ensemble(est_tmp, mat_tmp, cut=cut)

            # if all predictions are zero
            if sum(pred_tmp) == 0:

                # make a zero matrix
                pred_mat = np.zeros((len(lat_tmp), len(long_tmp)), order='F', dtype=int)

            # else
            else:

                # make a matrix of the predicted values
                pred_mat = np.reshape(pred_tmp, (len(lat_tmp), len(long_tmp)), order='F')

            # delete a file if it exists
            txt_path = out_dir + '/' + str(uid) + '_' + str(date) + '.txt'
            if os.path.exists(txt_path):
                os.remove(txt_path)

            # write the matrix as a esri ascii file
            txt_header = 'ncols ' + str(len(long_tmp)) + '\n' + \
                         'nrows ' + str(len(lat_tmp)) + '\n' + \
                         'xllcenter ' + str(long_tmp[0]) + '\n' + \
                         'yllcenter ' + str(lat_tmp[-1]) + '\n' + \
                         'cellsize ' + str(res) + '\n' + \
                         'nodata_value -999' + '\n'
            np.savetxt(txt_path, pred_mat, fmt='%i', delimiter=' ', header=txt_header, comments='')

            # add the text path
            txt_files.append(txt_path)

    # return the list of file paths
    return txt_files



