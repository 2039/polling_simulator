"""
"""

from argparse import ArgumentParser
from plotting import plot_population, plot_poll, plot_single_poll, plot_polls, plot_multiple_polls
from random import seed
from polling import Population


# Parse command line arguments
parser = ArgumentParser()

parser.add_argument("-S", "--seed", default=0, type=int, help="Set seed")
parser.add_argument("-P", "--plot", default=False, help="Plot one of [population|poll|polls]")
parser.add_argument("-A", "--animate", action="store_true", help="Animate plot")
parser.add_argument("-s", "--save", default=False, help="Save plot")

# kwargs
parser.add_argument("-v", "--voters", default=5000, type=int, help="Number of voters in poll")
parser.add_argument("-t", "--tallies", default=500, type=int, help="Number of tallies/districts (poll splits)")
parser.add_argument("-p", "--polls", default=600, type=int, help="Number of polls")
parser.add_argument("-a", "--alpha", default=0.95, type=float, help="Significance level")
parser.add_argument("-r", "--replace", action="store_true", help="Sample with replacement")

options = parser.parse_args()

# Set seed
seed(options.seed)



_kwargs = dict(
    without_replacement = not options.replace,
    voters              = options.voters,
    tallies             = options.tallies,
    polls               = options.polls,
    alpha               = options.alpha,
)



# Stortingsvalgresultat 2017
parties = Population({
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

from inspect import signature
params = lambda foo: signature(foo).parameters.keys()
kwargs = lambda foo: {k: _kwargs[k] for k in params(foo) & _kwargs.keys()}


if options.plot == "population":
    plot_population(parties, party_color, save=options.save)
if options.plot == "poll":
    if not options.animate:
        plot_poll(parties, party_color, **kwargs(plot_poll), save=options.save)
    else:
        plot_single_poll(parties, party_color, **kwargs(plot_single_poll), save=options.save)
if options.plot == "polls":
    if not options.animate:
        plot_polls(parties, party_color, **kwargs(plot_polls), save=options.save)
    else:
        plot_multiple_polls(parties, party_color, **kwargs(plot_multiple_polls), save=options.save)
