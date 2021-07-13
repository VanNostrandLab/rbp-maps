#!/bin/env python
# encoding: utf-8
"""

This module contains the LineObject class whose attributes describe
lines that will be plotted.

Created on May 3, 2017

@author: brianyee
"""

from density import normalization_functions as norm
from scipy import stats
import sys
import os
import numpy as np


class LineObject():
    def __init__(
            self, event_matrix, annotation_src_file, conf,
            color, min_event_threshold, num_events, label
    ):
        """

        Parameters
        ----------
        event_matrix: pandas.DataFrame
        annotation_src_file: basestring
        conf: float
        color:
        min_event_threshold: int
        divide_hist: boolean
        num_events: list
        """
        # TODO: change this entire piece of code
        self.event_matrix = event_matrix # normalized matrix of density or peak values.
        self.conf = conf # confidence cutoff for removing outliers
        self.annotation_src_file = annotation_src_file  # annotation_src_file file
        self.num_events = num_events # number of events

        self.label = self._parse_filename_for_plot() # cleans up the text for legend labels
        self.file_label = self._parse_filename() if label is None else label# cleans up the text for legend labels

        # print("number of events (avg for all positions) found for {}: {}".format(
        #     self.file_label, sum(self.num_events)/len(self.num_events))
        # )

        self.dim = False if sum(self.num_events)/len(self.num_events) > min_event_threshold else True # Dims the line. True if the number of events falls below some minimum event threshold
        self.p_values = []
        self.color = color
        self.values = list(event_matrix.sum())



    def has_pvalues(self):
        """
        Returns whether or not we did significance testing using this line.
        This prevents lines (such as background lines) from outputting empty
        files

        Returns
        -------
        has_pvalues : bool
            True if the line was selected as a test line, False otherwise.

        """
        return True if self.p_values != [] else False

    def _parse_filename_for_plot(self):
        """
        Removes any extra stuff that we might not want in the name.

        Parameters
        ----------
        annotation_src_file : basestring

        Returns
        -------
        nice_label : basestring
        """
        if 'shorter-isoform' in os.path.basename(self.annotation_src_file):
            if 'controls' in os.path.basename(self.annotation_src_file):
                firstparsed_string = 'short-isoform-in->50%-controls'
            else:
                firstparsed_string = 'short-isoform-upon-kd'
        elif 'longer-isoform' in os.path.basename(self.annotation_src_file):
            if 'controls' in os.path.basename(self.annotation_src_file):
                firstparsed_string = 'long-isoform-in->50%-controls'
            else:
                firstparsed_string = 'long-isoform-upon-kd'
        elif 'psi isoform' in os.path.basename(self.annotation_src_file):
            firstparsed_string = 'mixed-psi-isoform-in->50%-controls'
        elif 'included-upon-knockdown' in os.path.basename(self.annotation_src_file):
            firstparsed_string = 'included-upon-knockdown'
        elif 'excluded-upon-knockdown' in os.path.basename(self.annotation_src_file):
            firstparsed_string = 'excluded-upon-knockdown'
        else:
            firstparsed_string = os.path.basename(self.annotation_src_file)

        firstparsed_string = firstparsed_string.replace(
            'HepG2_', '').replace(
            'K562_', '').replace(
            'HepG2-', '').replace(
            'K562-', '').replace(
            '-', ' ').replace(
            '_', ' ').replace(
            '.tpm1','').replace('hg19_v19_','') + " ({} events)".format(
            (sum(self.num_events) / len(self.num_events))
        )
        firstparsed_string = '{}{}'.format(
            firstparsed_string[0].upper(), firstparsed_string[1:]
        )
        return os.path.splitext(
            firstparsed_string
        )[0]

    def _parse_filename(self):
        """
        Deprecated function.
        Returns simplified version of the name
        Returns
        -------

        """
        return os.path.basename(self.annotation_src_file)



    def calculate_and_set_significance(self, bg_matrix, test='mannwhitneyu'):
        pass


    def _set_std_error_boundaries(self, bottom_values=None, top_values=None):
        """
        Returns the +/- error boundaries given a list of values (means)

        Parameters
        ----------
        means
        error

        Returns
        -------

        """
        for tv in range(0, len(top_values)):
            if np.isnan(top_values[tv]):
                top_values[tv] = self.means[tv] # + abs(self.means[tv]*0.1)
            if np.isnan(bottom_values[tv]):
                bottom_values[tv] = self.means[tv] # - abs(self.means[tv]*0.1)

        self.error_pos = top_values
        self.error_neg = bottom_values
        self.max = max(self.error_pos)
        self.min = min(self.error_neg)
        return 0

    def _get_std_error_boundaries(self, values):
        """
        Sets the std error upper/lower boundaries given a mean and standard error

        Parameters
        ----------
        hist
        n

        Returns
        -------

        """
        mean_events = sum(self.num_events) / len(self.num_events)
        plus = [x + y * mean_events for x, y in zip(
            values, norm.std_error(
                values, self.num_events)
        )]
        minus = [x - y * mean_events for x, y in zip(
            values, norm.std_error(
                values, self.num_events)
        )]
        return plus, minus, max(plus), min(minus)

class PeakLine(LineObject):
    def __init__(
            self, event_matrix, annotation_src_file, conf,
            color, min_event_threshold, num_events, label,
            divide_hist=True
    ):
        """

        Parameters
        ----------
        self
        event_matrix
        annotation_src_file
        conf
        color
        min_event_threshold

        Returns
        -------

        """
        LineObject.__init__(self, event_matrix, annotation_src_file, conf,
            color, min_event_threshold, num_events, label)
        self.hist = self._get_hist()
        self.values = norm.divide_by_num_events(self._get_hist(), self.num_events)
        self.means = self.values  # TODO: resolve
        self.error_pos, self.error_neg, self.max, self.min = self._get_std_error_boundaries(
            self.values, divide_hist)  # upper and lower boundaries for error

    def has_hist(self):
        """
        Returns whether or not this line contains a histogram of peaks.
        Density plots do not contain a histogram of peaks

        Returns
        -------
        has_hist : bool
            True if the line was based on a histogram of peaks, else False.

        """
        return True

    def _get_hist(self):
        """

        Returns
        -------
        hist: list
            list of all values summed across each position (column).
        """
        return list(self.event_matrix.sum())


    def _get_std_error_boundaries(self, values, divide):
        """
        Sets the std error upper/lower boundaries given a mean and standard error

        Parameters
        ----------
        hist
        n

        Returns
        -------

        """
        if divide:
            plus = [x + y for x, y in zip(
                values, norm.std_error(
                    self.hist, self.num_events)
            )]
            minus = [x - y for x, y in zip(
                values, norm.std_error(
                    self.hist, self.num_events)
            )]
        else:  # just multiply by the number of events to get the true error
            plus = [x + y * self.num_events for x, y in zip(
                values, norm.std_error(
                    values, self.num_events)
            )]
            minus = [x - y * self.num_events for x, y in zip(
                values, norm.std_error(
                    values, self.num_events)
            )]
        return plus, minus, max(plus), min(minus)

    def calculate_fisher(self, bg_matrix):
        p_values = []
        bg_num_events = bg_matrix.shape[0]
        bg_hist = list(bg_matrix.sum())
        for i in range(0, len(self.hist)):
            total_peak = self.hist[i]  # total peaks at position i
            total_without_peak = sum(self.num_events)/len(self.num_events) - total_peak
            bg_total_peak = bg_hist[i]
            bg_total_without_peak = bg_num_events - bg_total_peak
            contingency_table = [
                [total_peak, total_without_peak],
                [bg_total_peak, bg_total_without_peak]
            ]

            odds, p = stats.fisher_exact(contingency_table)
            p_values.append(-1 * np.log10(p))
        return p_values

    def calculate_and_set_significance(self, bg_matrix, test='fisher'):
        if test == 'fisher':
            self.p_values = self.calculate_fisher(bg_matrix)

    def has_mean(self):
        return False


class DensityLine(LineObject):
    def __init__(
            self, event_matrix, annotation_src_file, conf,
            color, min_event_threshold, num_events, label
    ):
        """

        Parameters
        ----------
        self
        event_matrix
        annotation_src_file
        conf
        color
        min_event_threshold

        Returns
        -------

        """
        LineObject.__init__(self, event_matrix, annotation_src_file, conf,
                            color, min_event_threshold, num_events, label)
        self.hist = []
        self.means, \
        self.sems, \
        self.std, \
        self.outlier_removed_matrix = self._get_means_and_sems()  # 3 lists, 1 dataframe
        self.error_pos, self.error_neg, self.max, self.min = self._get_std_error_boundaries()  # upper and lower boundaries for error
        self.values = self.means

    def _get_means_and_sems(self):
        """
        Sets the means and standard error values after outlier
        removal. Replaces remove_outliers.

        Parameters
        ----------
        df : pandas.DataFrame
            table of densities or values
        conf : float
            keep {conf}% of densities present at every given position

        Returns
        -------

        means : list
            mean value for each position in the dataframe df
        sems : list
            standard error of the mean
        std : list
            standard deviation of the mean
        outlier_removed_df : pandas.DataFrame
            dataframe 'masked' of outliers
        """

        means, sems, std_deviation, outlier_removed_df = norm.get_means_and_sems(
            self.event_matrix, self.conf
        )
        for i in range(0, len(sems)):
            if np.isnan(sems[i]):
                print(
                "Warning: encountered no standard error for position: "
                "{}.".format(i))
                sems[i] = 0
            if np.isnan(std_deviation[i]):
                std_deviation[i] = 0
        return means, sems, std_deviation, outlier_removed_df


    def _get_std_error_boundaries(self):
        """
        Returns the +/- error boundaries given a list of values (means)

        Parameters
        ----------
        means
        error

        Returns
        -------

        """
        pos = [x + y for x, y in zip(self.means, self.sems)]
        neg = [x - y for x, y in zip(self.means, self.sems)]
        return pos, neg, max(pos), min(neg)

    def calculate_and_set_significance(self, bg_matrix, test='mannwhitneyu'):
        if test == 'mannwhitneyu':
            self.p_values = self.calculate_mannwhitneyu(bg_matrix)
        elif test == 'ks':
            self.p_values = self.calculate_ks(bg_matrix)
        elif test == 'zscore':
            self.p_values = self.calculate_zscore(bg_matrix)

    def calculate_ks(self, bg_matrix):
        """
        Given a background event matrix, compute distribution
        and calculate 2-sample KS test

        Parameters
        ----------
        bg_matrix : pandas.DataFrame()
            a position matrix (event = row, positon = col)

        Returns
        -------
        list of -log10 p-values for each position

        """
        p_values = []
        _, _, _, test_matrix = norm.get_means_and_sems_with_merged(self.event_matrix, conf=self.conf)
        _, _, _, bg_matrix = norm.get_means_and_sems_with_merged(bg_matrix, conf=self.conf)

        for position in self.event_matrix.columns:
            _, p = stats.ks_2samp(
                test_matrix[position], bg_matrix[position]
            )
            p_values.append(-1 * np.log10(p))
        return p_values

    def calculate_zscore(self, bg_matrix):

        bg_means, bg_sems, bg_dev, _ = norm.get_means_and_sems(
            bg_matrix, self.conf
        )
        p_values = []
        for i in range(0, len(self.means)):
            z_score = (self.means[i] - bg_means[i]) / bg_dev[i]
            p_values.append(z_score)
        return p_values

    def calculate_mannwhitneyu(self, bg_matrix):
        """
        Given a background event matrix, compute distribution
        and calculate mann whitney u 1 tailed greater test

        Parameters
        ----------
        bg_matrix : pandas.DataFrame()
            a position matrix (event = row, positon = col)

        Returns
        -------
        list of -log10 p-values for each position

        """
        p_values = []
        _, _, _, test_matrix = norm.get_means_and_sems_with_merged(self.event_matrix, conf=self.conf)
        _, _, _, bg_matrix = norm.get_means_and_sems_with_merged(bg_matrix, conf=self.conf)
        for position in test_matrix.columns:
            _, p = stats.mannwhitneyu(
                test_matrix[position], bg_matrix[position],
                alternative='greater'
            )
            p_values.append(-1 * np.log10(p))
        return p_values

    def has_hist(self):
        """
        Returns whether or not this line contains a histogram of peaks.
        Density plots do not contain a histogram of peaks

        Returns
        -------
        has_hist : bool
            True if the line was based on a histogram of peaks, else False.

        """
        return False

    def has_mean(self):
        return True


def create_line(event_matrix, annotation_src_file, conf, color,
                min_event_threshold, map_type, num_events, label=None):
    if map_type == 'peak':
        return PeakLine(
            event_matrix=event_matrix,
            annotation_src_file=annotation_src_file,
            conf=1,
            color=color,
            min_event_threshold=min_event_threshold,
            num_events=num_events,
            label=label
        )
    elif map_type == 'density' or map_type == 'phastcon':
        return DensityLine(
            event_matrix=event_matrix,
            annotation_src_file=annotation_src_file,
            conf=conf,
            color=color,
            min_event_threshold=min_event_threshold,
            num_events=num_events,
            label=label
        )
