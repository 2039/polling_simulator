"""
"""

from polling import Population, votes, Tally, error
from collections import Counter
from argparse import ArgumentParser
from random import seed
from math import log
from color import Color

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument("-s", "--seed", default=0, type=int, help="Set seed.")
options = parser.parse_args()

# Set seed
seed(options.seed)


# Stortingsvalgresultat 2017
population = Population({
    "R"   :  70_522,
    "SV"  : 175_222,
    "AP"  : 800_947,
    "SP"  : 302_017,
    "MDG" :  94_788,
    "KRF" : 122_797,
    "V"   : 127_910,
    "H"   : 732_895,
    "FRP" : 444_681,
})

# colours from https://www.nrk.no/valg/2017/resultat/
party_color = {
    "R"   : "#990014",
    "SV"  : "#d94abf",
    "AP"  : "#e51c30",
    "SP"  : "#a5cd39",
    "MDG" : "#3d8704",
    "KRF" : "#f0b618",
    "V"   : "#24b38c",
    "H"   : "#00b9f2",
    "FRP" : "#005799",
}


# ===

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import gridspec

def plot_single_poll():
    TOTAL = sum(population.weights)
    VOTERS = 1_000 #sum(population.weights) #100_000
    TALLIES = 500
    #ERROR = error(p=0.5, n=VOTERS, N=TOTAL, alpha=0.95)
    #VOTE_LIMIT = max(population.weights) * 1.1 #(1.1 + ERROR)


    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 29], hspace=0)

    ax = fig.add_subplot(gs[1])

    progress = fig.add_subplot(gs[0])
    progress.set_xticks([], [])
    progress.set_yticks([], [])

    fig.tight_layout()

    for patch in (fig, ax):
        patch.patch.set_alpha(0.0)

    # ---

    # bars

    indexes = list(population.group_index.values())
    heights = [0]*len(population)
    tally = Tally(population, VOTERS, TALLIES, without_replacement=True)

    bars = ax.bar(indexes, heights, color=party_color.values())
    errors = [ax.errorbar(i, heights[i], yerr=1000, capsize=15, capthick=1, fmt='none', color=Color(color).darken(20)) for i, color in enumerate(party_color.values())]

    ax.set_ylim(0, VOTERS)

    # pbar

    pbar = progress.barh(0.5, 0, height=1, color='orange')
    progress.set_xlim(0, 1)

    def update_errorbars(errorbars, bars):
        # wtf matplotlib
        # https://stackoverflow.com/questions/25210723/matplotlib-set-data-for-errorbar-plot
        # https://stackoverflow.com/questions/21912197/setting-different-error-bar-colors-in-bar-plot-in-matplotlib

        current_vote_count = sum(bar.get_height() for bar in bars)

        for errorbar, bar, group in zip(errorbars, bars, population.groups):
            ln, (erry_top, erry_bot), (bary,) = errorbar

            err_pct = error(population.p(group), current_vote_count, TOTAL, alpha=0.95)
            err = err_pct * current_vote_count

            #ln.set_ydata(bar.get_height())

            top = bar.get_height() + err
            bot = bar.get_height() - err

            erry_top.set_ydata(top)
            erry_bot.set_ydata(bot)

            i = bary.get_segments()[0][0,0]

            bary.set_segments([[[i,top], [i, bot]]])

    def init():
        # useless unless blit is True

        ax.set_xlim(0-0.5, len(population)-0.5)

        ax.set_xticks(range(len(population)))
        ax.set_xticklabels(population.groups)

        return bars



    def update(tally):
        for group in tally:
            bar = bars[population.group_index[group]]

            bar.set_height(bar.get_height() + tally[group])


        update_errorbars(errors, bars)

        current_vote_count = sum(bar.get_height() for bar in bars)


        pbar[0].set_width(current_vote_count/VOTERS)

        vote_count = tuple(bar.get_height() for bar in bars)
        err = error(p=0.5, n=sum(vote_count), N=TOTAL, alpha=0.99)
        M = int(max(vote_count) * (1.1 + err))
        Mint = round(M, -int(log(M, 10))+1)

        ax.set_ylim(0, M)
        ax.set_yticks(range(0, M, max(1, M//10)))

        return bars



    frame_length_ms = 10
    anim = FuncAnimation(
        fig, update, frames=tally, repeat=True, repeat_delay=1_000,
        init_func=init, interval=frame_length_ms, blit=False,
    )

    plt.show()


def plot_multiple_polls():
    pass

plot_single_poll()
