import pickle
from pathlib import Path

import numpy as np

from mab.posteriors import Posteriors
from mab.sampling import Sampling


class BFTS(Sampling):
    """Boundary Focused Thompson Sampling

    From: https://github.com/plibin-vub/bfts

    Attributes:
        posteriors: The Posteriors to apply the sampling method to
        top_m: The number of posteriors to provide as the top m best posteriors.
        seed: The seed for initialisation.
    """
    def __init__(self, posteriors: Posteriors, top_m, seed):
        # Super call
        super(BFTS, self).__init__(posteriors, seed)
        #
        self.m = top_m
        self.has_ranking = True
        self.sample_ordering = None
        self.current_ranking = None

    @staticmethod
    def new(top_m):
        """Workaround to add a given top_m arms to the sampling method"""
        return lambda posteriors, seed: BFTS(posteriors, top_m, seed)

    def sample_arm(self, t):
        """Sample an arm based on the sampling method."""
        # Sample all arms and order them
        theta = self.posteriors.sample_all(t)
        order = np.argsort(-np.array(theta))
        # Choose an arm from the boundary (top_m boundary)
        arm_i = order[self.m - 1 + np.random.choice([0, 1])]

        self.sample_ordering = order
        self.current_ranking = self.top_m(t)
        print(f"=== TOP_M arms at timestep {t}: {self.current_ranking} ===")

        return arm_i

    def top_m(self, t):
        """Get the top m arms at timestep t"""
        # Get the means per arm
        means = self.posteriors.means_per_arm(t)
        if isinstance(means, list):
            means = np.array(means)
        return np.argsort(-means)[0:self.m]

    def save(self, path: Path):
        """Save the sampling method to the given file path"""
        with open(path, mode="wb") as file:
            data = [self.seed, self.rng, self.m, self.has_ranking, self.sample_ordering, self.current_ranking]
            pickle.dump(data, file)

    def load(self, path: Path):
        """Load the sampling method from the given file path"""
        with open(path, mode="rb") as file:
            data = pickle.load(file)
            self.seed, self.rng, self.m, self.has_ranking, self.sample_ordering, self.current_ranking = data
