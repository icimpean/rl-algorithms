import numpy as np
from sklearn.mixture import BayesianGaussianMixture
import pickle

from mab.posteriors import Posterior, SinglePosteriors


class GaussianMixturePosterior(Posterior):
    """A gaussian mixture posterior of a bandit's arms"""
    def __init__(self, k, tol, max_iter, seed=None):
        # Super call
        super(GaussianMixturePosterior, self).__init__(seed)
        # The internal mixture distribution
        self._mixture = BayesianGaussianMixture(n_components=k, covariance_type='full', reg_covar=1e-06,
                                                tol=tol, max_iter=max_iter, n_init=1, init_params='random',
                                                weight_concentration_prior_type='dirichlet_process',
                                                weight_concentration_prior=None, mean_precision_prior=None,
                                                mean_prior=None, degrees_of_freedom_prior=None, covariance_prior=None,
                                                random_state=seed,
                                                warm_start=True,
                                                verbose=0, verbose_interval=10)

    @staticmethod
    def new(seed, k, tol, max_iter):
        return GaussianMixturePosterior(k, tol, max_iter, seed)

    def update(self, reward, t):
        self.rewards.append(reward)
        X = np.array(self.rewards)
        # Data contains a single feature (reward)
        X = X.reshape(-1, 1)
        # sklearn requires 2 samples minimum per fit
        if len(X) > 1:
            self._mixture.fit(X)

    def sample(self, t):
        X, y = self._mixture.sample()
        X = X[0][0]
        return X

    def save(self, path):
        with open(path, 'wb') as file:
            pickle.dump(self._mixture, file)

    def load(self, path):
        with open(path, 'rb') as file:
            self._mixture = pickle.load(file)


class BGMPosteriors(SinglePosteriors):
    """A Bayesian Gaussian Mixture Posterior for a given number of bandit arms."""
    def __init__(self, nr_arms, seed=None, k=2, tol=0.001, max_iter=100):
        self.k = k
        self.tol = tol
        self.max_iter = max_iter
        super(BGMPosteriors, self).__init__(nr_arms, GaussianMixturePosterior, seed)

    def _create_posteriors(self, seed, posterior_type):
        return [posterior_type.new(seed + i, self.k, self.tol, self.max_iter) for i in range(self.nr_arms)]
