from polling import votes, poll, Tally, error
from collections import Counter
from math import log, inf
from color import Color

def create_folder_if_not_exists(name):
    from pathlib import Path
    folder = Path(f"./{name}")
    folder.mkdir(parents=True, exist_ok=True)
    return folder

# ===

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import gridspec

def plot_population(population, group_color, save=False):
    largest_group = max(population, key=lambda g: population[g])

    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)

    ax = fig.add_subplot(gs[0])
    fig.tight_layout()

    for patch in (fig, ax):
        patch.patch.set_alpha(0.0)

    # ---

    indexes = list(population.group_index.values())
    bars = ax.bar(indexes, population.weights, color=group_color.values())

    true_p = ax.hlines(
        population.weights,
        [i-0.4 for i in range(len(population))],
        [i+0.4 for i in range(len(population))],
        colors=[Color(c).darken(10) for c in group_color.values()]
    )

    ax.set_ylim(0, 1.1 * population[largest_group])
    ax.set_xlim(0-0.5, len(population)-0.5)

    ax.set_xticks(range(len(population)))
    ax.set_xticklabels(population.groups)

    ax.set_title(f"The population distribution")

    if save:
        folder = create_folder_if_not_exists("figures")
        fig.savefig(f"{folder / save}.png", format="png")
    plt.show()


# ===


def plot_poll(population, group_color, voters=None, alpha=0.95, without_replacement=True, save=False):
    if voters is None: voters = sum(population.weights)
    largest_group = max(population, key=lambda g: population[g])

    size_limit = population.size if without_replacement else inf


    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)

    ax = fig.add_subplot(gs[0])
    fig.tight_layout()

    for patch in (fig, ax):
        patch.patch.set_alpha(0.0)

    # ---

    # bars

    indexes = list(population.group_index.values())
    results = poll(population, voters, without_replacement=without_replacement)
    heights = [results[group] for group in population]

    bars = ax.bar(indexes, heights, color=group_color.values())

    errors = [
        voters * error(population.p(group), voters, N=size_limit, alpha=0.95)
        for group in population
    ]
    for i, color in enumerate(group_color.values()):
        ax.errorbar(
            i, heights[i], yerr=errors[i],
            capsize=15, capthick=1, fmt='none', color=Color(color).darken(20)
        )

    true_p = ax.hlines(
        [voters * population.p(group) for group in population],
        [i-0.4 for i in indexes],
        [i+0.4 for i in indexes],
        colors=[Color(c).darken(10) for c in group_color.values()]
    )

    ax.set_ylim(0, 1.1 * voters * population.p(largest_group))

    ax.set_xlim(0-0.5, len(population)-0.5)

    ax.set_xticks(range(len(population)))
    ax.set_xticklabels(population.groups)

    ax.set_title(f"The poll distribution after asking {voters} voters, {alpha = }")

    if save:
        folder = create_folder_if_not_exists("figures")
        fig.savefig(f"{folder / save}.png", format="png")
    plt.show()


# ===


def plot_single_poll(population, group_color, voters=None, tallies=500, alpha=0.95, without_replacement=True, save=False):
    if voters is None: voters = sum(population.weights) #100_000

    largest_group = max(population, key=lambda g: population[g])

    size_limit = population.size if without_replacement else inf


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
    tally = Tally(population, voters, tallies, without_replacement=without_replacement)

    bars = ax.bar(indexes, heights, color=group_color.values())
    errors = [
        ax.errorbar(i, heights[i], yerr=0, capsize=15, capthick=1, fmt='none', color=Color(color).darken(20)) for i, color in enumerate(group_color.values())
    ]
    true_p = ax.hlines(
        [population.size * population.p(group) for group in population],
        [i-0.4 for i in indexes],
        [i+0.4 for i in indexes],
        colors=[Color(c).darken(10) for c in group_color.values()]
    )

    ax.set_ylim(0, 1.1 * population.size * population.p(largest_group))

    # pbar

    pbar = progress.barh(0.5, 0, height=1, color='orange')[0]
    progress.set_xlim(0, 1)

    def update_errorbars(errorbars, bars):
        # wtf matplotlib
        # https://stackoverflow.com/questions/25210723/matplotlib-set-data-for-errorbar-plot
        # https://stackoverflow.com/questions/21912197/setting-different-error-bar-colors-in-bar-plot-in-matplotlib

        current_vote_count = sum(bar.get_height() for bar in bars)

        for errorbar, bar, group in zip(errorbars, bars, population.groups):
            ln, (erry_top, erry_bot), (bary,) = errorbar

            err_pct = error(population.p(group), current_vote_count, N=size_limit, alpha=alpha)
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

        # are you fucking shitting me you fucking piece of shit mpl
        # give me a hlines.set_ydata() function ffs
        p_est = [population.p(group)*current_vote_count for group in population]
        true_p.set_paths([
            [[i-0.4, y], [i+0.4, y]] for i, y in enumerate(p_est)
        ])

        pbar.set_width(current_vote_count/voters)

        # vote_count = tuple(bar.get_height() for bar in bars)
        # err = error(p=0.5, n=sum(vote_count), N=population.count, alpha=0.99)
        # M = int(max(vote_count) * (1.1 + err))
        # Mint = round(M, -int(log(M, 10))+1)

        M = int(1.1*current_vote_count*population.p(largest_group))

        ax.set_ylim(0, M)
        ax.set_yticks(range(0, M, max(1, M//10)))

        return bars


    progress.set_title(f"Counting votes in packs of {voters//tallies}, {alpha = }")

    frame_length_ms = 10
    anim = FuncAnimation(
        fig, update, frames=tally, repeat=True, repeat_delay=1_000,
        init_func=init, interval=frame_length_ms, blit=False, save_count=tallies,
    )

    if save:
        folder = create_folder_if_not_exists("figures")
        anim.save(f"{folder / save}.webm", codec="png", extra_args=["-vcodec", "libvpx-vp9"], fps=20)
    plt.show()




# ===


def plot_polls(population, group_color, voters=None, polls=500, alpha=0.95, without_replacement=True, save=False):
    if voters is None: voters = sum(population.weights)
    largest_group = max(population, key=lambda g: population[g])

    size_limit = population.size if without_replacement else inf


    fig = plt.figure()
    gs = gridspec.GridSpec(1, 1)

    ax = fig.add_subplot(gs[0])
    fig.tight_layout()

    for patch in (fig, ax):
        patch.patch.set_alpha(0.0)

    # ---

    errors = [
        voters * error(population.p(group), voters, N=size_limit, alpha=alpha)
        for group in population
    ]
    for i, color in enumerate(group_color.values()):
        ax.errorbar(
            i,
            voters * population.weights[i]/population.size,
            yerr=errors[i],
            capsize=15,
            capthick=1,
            fmt='none',
            color=Color(color).darken(20)
        )

    indexes = list(population.group_index.values())
    for _poll in range(polls):
        results = poll(population, voters, without_replacement=without_replacement)

        estimate_p = ax.hlines(
            [results[group] for group in population],
            [i-0.1 for i in indexes],
            [i+0.1 for i in indexes],
            colors=[Color(c).darken(10) for c in group_color.values()],
            alpha=0.2,
        )

    ax.set_ylim(0, 1.1 * voters * (population.p(largest_group) + error(population.p(largest_group), voters, N=size_limit, alpha=0.99)))

    ax.set_xlim(0-0.5, len(population)-0.5)

    ax.set_xticks(range(len(population)))
    ax.set_xticklabels(population.groups)

    ax.set_title(f"The results of {polls} polls with {voters} voters, {alpha = }")

    if save:
        folder = create_folder_if_not_exists("figures")
        fig.savefig(f"{folder / save}.png", format="png")
    plt.show()


# ===


def plot_multiple_polls(population, group_color, voters=None, polls=500, alpha=0.95, without_replacement=True, save=False):
    if voters is None: voters = sum(population.weights) #100_000

    largest_group = max(population, key=lambda g: population[g])

    size_limit = population.size if without_replacement else inf


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


    indexes = list(population.group_index.values())
    heights = [0]*len(population)

    errors = [
        voters * error(population.p(group), voters, N=size_limit, alpha=alpha)
        for group in population
    ]
    for i, color in enumerate(group_color.values()):
        ax.errorbar(
            i,
            voters * population.weights[i]/population.size,
            yerr=errors[i],
            capsize=15,
            capthick=1,
            fmt='none',
            color=Color(color).darken(20)
        )

    ax.set_ylim(0, 1.1 * voters * (population.p(largest_group) + error(population.p(largest_group), voters, N=size_limit, alpha=0.99)))

    # pbar

    pbar = progress.barh(0.5, 0, height=1, color='orange')[0]
    progress.set_xlim(0, 1)


    def init():
        # useless unless blit is True

        ax.set_xlim(0-0.5, len(population)-0.5)

        ax.set_xticks(range(len(population)))
        ax.set_xticklabels(population.groups)



    def update(poll_count):
        results = poll(population, voters, without_replacement=without_replacement)

        estimate_p = ax.hlines(
            [results[group] for group in population],
            [i-0.1 for i in indexes],
            [i+0.1 for i in indexes],
            colors=[Color(c).darken(10) for c in group_color.values()],
            alpha=0.2,
        )

        pbar.set_width(poll_count/polls)


    progress.set_title(f"Gathering poll results, {alpha = }")

    frame_length_ms = 10
    anim = FuncAnimation(
        fig, update, frames=range(polls), repeat=True, repeat_delay=1_000,
        init_func=init, interval=frame_length_ms, blit=False, save_count=polls
    )

    if save:
        folder = create_folder_if_not_exists("figures")
        anim.save(f"{folder / save}.webm", codec="png", extra_args=["-vcodec", "libvpx-vp9"], fps=20)
    plt.show()
