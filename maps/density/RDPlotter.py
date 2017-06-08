import matplotlib
matplotlib.use('Agg')

from matplotlib import rc
rc('text', usetex=False)
matplotlib.rcParams['svg.fonttype'] = 'none'
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import seaborn as sns
from collections import OrderedDict, defaultdict

sns.set_style("whitegrid")
sns.set_context("talk", font_scale=1.2)

MIN_N_THRESHOLD = 100

COLOR_PALETTE = sns.color_palette("hls", 8)
BG1_COLOR = 'black' # COLOR_PALETTE['black']
BG2_COLOR = COLOR_PALETTE[6]
BG3_COLOR = COLOR_PALETTE[7]
BG4_COLOR = COLOR_PALETTE[4]
POS_COLOR = COLOR_PALETTE[0]
NEG_COLOR = COLOR_PALETTE[5]

COLORS = [POS_COLOR, NEG_COLOR, BG1_COLOR, BG2_COLOR, BG3_COLOR, BG4_COLOR]

import intervals
import misc


class _Plotter:
    def __init__(self, means, sems, num_regions=1):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        self.means = means
        self.sems = sems
        self.num_regions = num_regions
        self.cols = COLORS  # TODO remove it

    def plot(self, ax):
        c = 0
        for filename, mean in self.means.iteritems():
            ax.plot(mean['means'], color=self.cols[c],
                    label=misc.sane(filename))
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)

            c += 1
        ax.legend(
            bbox_to_anchor=(
                0., 1.2, 1., .102), loc=1, mode="expand", borderaxespad=0.
        )


class _GenericPlotter(_Plotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        ns : dict
            {filename:int}
        """
        _Plotter.__init__(self, means, sems, num_regions)
        sns.despine(left=True, right=True)

    def plot(self, axs):
        c = 0

        for filename, mean in self.means.iteritems():
            # print('filename: [{}]'.format(filename))
            # TODO: turn this into an option
            """
            if "INCLUDED" in filename.upper():
                color = self.cols[0]
            elif "EXCLUDED" in filename.upper():
                color = self.cols[5]
            else:
                color = 'black'
            """
            total_len = len(mean['means'])

            region_len = total_len / self.num_regions
            regions = intervals.split(mean['means'], self.num_regions)
            for i in range(0, self.num_regions):
                # print("filename: {}".format(filename))
                if mean['nums'] < MIN_N_THRESHOLD:
                    alpha = 0.3
                else:
                    alpha = 1

                axs[i].plot(
                    # regions[i], color=color, label=misc.sane(filename)
                    regions[i], color=self.cols[c], label=
                        self.trim_filename(filename) + " ({} events)".format(mean['nums'],
                    ),
                    alpha=alpha,
                    linewidth=0.8
                )
                self.renumber_xaxis(i, region_len, axs)

            c += 1
        axs[0].set_ylabel("Normalized Density")

        leg = axs[0].legend(
            bbox_to_anchor=(1.4, -0.2), loc=1, mode="expand",
            borderaxespad=0., ncol=2
        )
        for legobj in leg.legendHandles:
            legobj.set_label(legobj.get_label()[0])
            legobj.set_linewidth(4.0)

    def trim_filename(self, filename):
        return filename.replace('-',' ').replace('_',' ').replace('HepG2','').replace('K562','')

    def renumber_xaxis(self, i, region_len, axs):
        """
        Renames x axis to fit up/downstream directionality.

        Parameters
        ----------
        i : int
            number of regions
        region_len : int
            length of the entire region
        axs : matplotib axes[]
            list of matplotlib subplot axes
        Returns
        -------

        """
        if i % 2 == 1:
            axs[i].set_xticklabels(xrange(-region_len, 1, 50))


class _SEPlotter(_GenericPlotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        _GenericPlotter.__init__(self, means, sems, num_regions)

    def renumber_xaxis(self, i, region_len, axs, stepper=50):
        if i % 2 == 1:
            axs[i].set_xticks(xrange(0, region_len+1, stepper))
            axs[i].set_xticklabels(['-{}'.format(region_len-stepper), '', '', '', '', '', '-{}'.format(stepper), '0'])
        else:
            axs[i].set_xticks(xrange(0, region_len+1, stepper))
            axs[i].set_xticklabels(['0', '{}'.format(stepper), '', '', '', '', '', '{}'.format(region_len-stepper)])

        for tick in axs[i].get_xticklabels():
            tick.set_rotation(90)


class _A3SSPlotter(_GenericPlotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        _GenericPlotter.__init__(self, means, sems, num_regions)

    def renumber_xaxis(self, i, region_len, axs):
        axs[0].set_xticklabels(xrange(-50, region_len+51, 50))
        axs[1].set_xticklabels(xrange(-region_len+50, 51, 50))
        axs[2].set_xticklabels(xrange(-region_len+50, 51, 50))


class _A5SSPlotter(_GenericPlotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        _GenericPlotter.__init__(self, means, sems, num_regions)

    def renumber_xaxis(self, i, region_len, axs):
        axs[0].set_xticklabels(xrange(-50, region_len + 51, 50))
        axs[1].set_xticklabels(xrange(-50, region_len + 51, 50))
        axs[2].set_xticklabels(xrange(-region_len, 1, 50))


class _RetainedIntronPlotter(_GenericPlotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        _GenericPlotter.__init__(self, means, sems, num_regions)

    def renumber_xaxis(self, i, region_len, axs):
        """
        Renames x axis to fit up/downstream directionality.

        Parameters
        ----------
        i : int
            number of regions
        region_len : int
            length of the entire region
        axs : matplotib axes[]
            list of matplotlib subplot axes
        Returns
        -------

        """
        if i % 2 == 1:
            axs[i].set_xticklabels(xrange(-region_len, 1, 50))


class _UnscaledCDSPlotter(_GenericPlotter):
    def __init__(self, means, sems, num_regions):
        """
        means : dict
            {filename:pandas.Series}
        sems : dict
            {filename:pandas.Series}
        """
        _GenericPlotter.__init__(self, means, sems, num_regions)

    def renumber_xaxis(self, i, region_len, axs):
        """
        Renames x axis to fit up/downstream directionality.

        Parameters
        ----------
        i : int
            number of regions
        region_len : int
            length of the entire region
        axs : matplotib axes[]
            list of matplotlib subplot axes
        Returns
        -------

        """
        if i % 2 == 1:
            axs[i].set_xticklabels(xrange(-region_len, 1, 50))

def plot_across_multiple_axes(means, sems, axs):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of axes subplots

    Returns
    -------

    _GenericPlotter

    """
    plotter = _GenericPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_bed(means, sems, ax):
    """

    Parameters
    ----------
    means : list
        list of mean read densities
    sems : list
        list of standard error of means
    ax : matplotlib axes
        axes

    Returns
    -------

    _Plotter

    """
    plotter = _Plotter(means, sems)
    plotter.plot(ax)
    return plotter


def plot_exon(means, sems, axs):
    return plot_across_multiple_axes(means, sems, axs)


def plot_ri(means, sems, axs):
    plotter = _RetainedIntronPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_se(means, sems, axs):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of 4 axes subplots

    Returns
    -------

    """
    plotter = _SEPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_mxe(means, sems, axs):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of 6 axes subplots

    Returns
    -------

    """
    plotter = _GenericPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_a3ss(means, sems, axs):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of 3 axes subplots

    Returns
    -------

    """
    plotter = _A3SSPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_a5ss(means, sems, axs):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of 3 axes subplots

    Returns
    -------

    """
    plotter = _A5SSPlotter(means, sems, len(axs))
    plotter.plot(axs)
    return plotter


def plot_unscaled_cds(means, sems, axs, upstream_offset, downstream_offset):
    """

    Parameters
    ----------
    means : dict

    sems : dict
        std error for each annotation file
    axs : list
        list of 2 axes subplots

    Returns
    -------

    """
    plotter = _UnscaledCDSPlotter(
        means, sems, len(axs), upstream_offset, downstream_offset
    )
    plotter.plot(axs)
    return plotter