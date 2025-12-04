#!/usr/bin/env python3
"""
Gaussian Process Surrogate Model for Bayesian Architecture Optimization

Implements a Gaussian Process (GP) surrogate that models the relationship
between DAG features and an objective function (e.g., minimizing complexity,
context bottlenecks, or service coupling).

Key Features:
- Pure Python implementation (no sklearn dependency required)
- RBF (Radial Basis Function) kernel with automatic relevance determination
- Matern kernel for non-smooth objective functions
- Prior mean functions for incorporating domain knowledge
- Observation noise handling

The GP provides:
- Predicted mean (expected objective value)
- Predicted variance (uncertainty in prediction)

These are used by acquisition functions to balance exploration vs exploitation.

Usage:
    from surrogate_model import GaussianProcessSurrogate

    gp = GaussianProcessSurrogate(kernel="rbf", length_scale=1.0)
    gp.fit(X_train, y_train)
    mean, variance = gp.predict(X_test)

Version: 0.1.0
"""

import math
from typing import Dict, List, Optional, Tuple, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Optional numpy - provides significant speedup
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class KernelType(Enum):
    """Supported kernel types."""
    RBF = "rbf"
    MATERN_32 = "matern_32"
    MATERN_52 = "matern_52"
    RATIONAL_QUADRATIC = "rational_quadratic"


@dataclass
class GPConfig:
    """Configuration for Gaussian Process."""
    kernel: KernelType = KernelType.RBF
    length_scale: float = 1.0
    signal_variance: float = 1.0
    noise_variance: float = 1e-6
    normalize_y: bool = True
    prior_mean: float = 0.0


class GaussianProcessSurrogate:
    """
    Gaussian Process surrogate model for Bayesian optimization.

    Models the objective function f(x) as a Gaussian Process:
        f(x) ~ GP(m(x), k(x, x'))

    where m(x) is the mean function and k(x, x') is the covariance kernel.
    """

    def __init__(self, config: Optional[GPConfig] = None):
        """
        Initialize Gaussian Process.

        Args:
            config: GP configuration (kernel, hyperparameters)
        """
        self.config = config or GPConfig()

        # Training data
        self._X_train: Optional[List[List[float]]] = None
        self._y_train: Optional[List[float]] = None
        self._y_mean: float = 0.0
        self._y_std: float = 1.0

        # Precomputed matrices for efficiency
        self._K_inv: Optional[Any] = None
        self._alpha: Optional[Any] = None

    def fit(self, X: List[List[float]], y: List[float]) -> "GaussianProcessSurrogate":
        """
        Fit the GP to training data.

        Args:
            X: Feature vectors (n_samples x n_features)
            y: Objective values (n_samples,)

        Returns:
            self for chaining
        """
        if len(X) != len(y):
            raise ValueError(f"X and y must have same length: {len(X)} vs {len(y)}")

        if len(X) == 0:
            raise ValueError("Cannot fit GP with no data")

        self._X_train = [list(x) for x in X]

        # Normalize y if configured
        if self.config.normalize_y:
            self._y_mean = sum(y) / len(y)
            variance = sum((yi - self._y_mean) ** 2 for yi in y) / len(y)
            self._y_std = math.sqrt(variance) if variance > 0 else 1.0
            self._y_train = [(yi - self._y_mean) / self._y_std for yi in y]
        else:
            self._y_train = list(y)
            self._y_mean = 0.0
            self._y_std = 1.0

        # Compute kernel matrix and its inverse
        self._precompute_matrices()

        return self

    def predict(
        self,
        X: List[List[float]],
        return_std: bool = True
    ) -> Union[Tuple[List[float], List[float]], List[float]]:
        """
        Predict mean and (optionally) standard deviation.

        Args:
            X: Feature vectors to predict (n_samples x n_features)
            return_std: Whether to return standard deviations

        Returns:
            If return_std: (means, stds)
            Else: means only
        """
        if self._X_train is None:
            raise RuntimeError("GP must be fit before predicting")

        means = []
        stds = []

        for x in X:
            mean, var = self._predict_single(x)

            # Denormalize
            mean = mean * self._y_std + self._y_mean
            std = math.sqrt(max(0, var)) * self._y_std

            means.append(mean)
            stds.append(std)

        if return_std:
            return means, stds
        return means

    def _predict_single(self, x: List[float]) -> Tuple[float, float]:
        """Predict mean and variance for a single point."""
        if HAS_NUMPY:
            return self._predict_single_numpy(x)
        return self._predict_single_python(x)

    def _predict_single_numpy(self, x: List[float]) -> Tuple[float, float]:
        """Predict using numpy for efficiency."""
        x = np.array(x)
        X_train = np.array(self._X_train)
        y_train = np.array(self._y_train)

        # k(x, X_train)
        k_star = np.array([self._kernel(x, xi) for xi in X_train])

        # Mean: k(x, X)^T @ K^{-1} @ y
        mean = float(k_star @ self._alpha)

        # Variance: k(x, x) - k(x, X)^T @ K^{-1} @ k(x, X)
        k_xx = self._kernel(x, x)
        v = np.linalg.solve(self._L, k_star)
        variance = k_xx - float(v @ v)

        return mean, max(0, variance)

    def _predict_single_python(self, x: List[float]) -> Tuple[float, float]:
        """Pure Python prediction (slower but no dependencies)."""
        n = len(self._X_train)

        # k(x, X_train)
        k_star = [self._kernel(x, self._X_train[i]) for i in range(n)]

        # Mean: k(x, X)^T @ alpha
        mean = sum(k_star[i] * self._alpha[i] for i in range(n))

        # Variance: k(x, x) - k(x, X)^T @ K^{-1} @ k(x, X)
        k_xx = self._kernel(x, x)
        v = self._solve_triangular(self._L, k_star)
        variance = k_xx - sum(vi * vi for vi in v)

        return mean, max(0, variance)

    def _precompute_matrices(self) -> None:
        """Precompute K^{-1} and alpha = K^{-1} @ y for efficiency."""
        n = len(self._X_train)

        if HAS_NUMPY:
            X = np.array(self._X_train)
            y = np.array(self._y_train)

            # Compute kernel matrix K
            K = np.zeros((n, n))
            for i in range(n):
                for j in range(i, n):
                    k_ij = self._kernel(X[i], X[j])
                    K[i, j] = k_ij
                    K[j, i] = k_ij

            # Add noise to diagonal
            K += self.config.noise_variance * np.eye(n)

            # Cholesky decomposition: K = L @ L^T
            self._L = np.linalg.cholesky(K)

            # alpha = K^{-1} @ y = L^{-T} @ L^{-1} @ y
            self._alpha = np.linalg.solve(self._L.T, np.linalg.solve(self._L, y))

        else:
            # Pure Python implementation
            K = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    k_ij = self._kernel(self._X_train[i], self._X_train[j])
                    K[i][j] = k_ij
                    K[j][i] = k_ij
                K[i][i] += self.config.noise_variance

            # Cholesky decomposition
            self._L = self._cholesky(K)

            # Solve for alpha
            z = self._solve_triangular(self._L, self._y_train)
            self._alpha = self._solve_triangular_transpose(self._L, z)

    def _kernel(self, x1: List[float], x2: List[float]) -> float:
        """Compute kernel value k(x1, x2)."""
        if self.config.kernel == KernelType.RBF:
            return self._rbf_kernel(x1, x2)
        elif self.config.kernel == KernelType.MATERN_32:
            return self._matern32_kernel(x1, x2)
        elif self.config.kernel == KernelType.MATERN_52:
            return self._matern52_kernel(x1, x2)
        elif self.config.kernel == KernelType.RATIONAL_QUADRATIC:
            return self._rational_quadratic_kernel(x1, x2)
        else:
            return self._rbf_kernel(x1, x2)

    def _rbf_kernel(self, x1: List[float], x2: List[float]) -> float:
        """
        RBF (Radial Basis Function) kernel.

        k(x1, x2) = sigma^2 * exp(-0.5 * ||x1 - x2||^2 / l^2)
        """
        sq_dist = sum((a - b) ** 2 for a, b in zip(x1, x2))
        return self.config.signal_variance * math.exp(
            -0.5 * sq_dist / (self.config.length_scale ** 2)
        )

    def _matern32_kernel(self, x1: List[float], x2: List[float]) -> float:
        """
        Matern 3/2 kernel (once differentiable).

        k(x1, x2) = sigma^2 * (1 + sqrt(3)*r/l) * exp(-sqrt(3)*r/l)
        """
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(x1, x2)))
        r = math.sqrt(3) * dist / self.config.length_scale
        return self.config.signal_variance * (1 + r) * math.exp(-r)

    def _matern52_kernel(self, x1: List[float], x2: List[float]) -> float:
        """
        Matern 5/2 kernel (twice differentiable).

        k(x1, x2) = sigma^2 * (1 + sqrt(5)*r/l + 5*r^2/(3*l^2)) * exp(-sqrt(5)*r/l)
        """
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(x1, x2)))
        r = math.sqrt(5) * dist / self.config.length_scale
        return self.config.signal_variance * (1 + r + r ** 2 / 3) * math.exp(-r)

    def _rational_quadratic_kernel(self, x1: List[float], x2: List[float]) -> float:
        """
        Rational Quadratic kernel (infinite mixture of RBFs).

        k(x1, x2) = sigma^2 * (1 + r^2 / (2*alpha*l^2))^{-alpha}

        with alpha=1.0 for simplicity
        """
        alpha = 1.0
        sq_dist = sum((a - b) ** 2 for a, b in zip(x1, x2))
        return self.config.signal_variance * (
            1 + sq_dist / (2 * alpha * self.config.length_scale ** 2)
        ) ** (-alpha)

    # Pure Python linear algebra helpers

    def _cholesky(self, A: List[List[float]]) -> List[List[float]]:
        """Cholesky decomposition: A = L @ L^T."""
        n = len(A)
        L = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1):
                s = sum(L[i][k] * L[j][k] for k in range(j))
                if i == j:
                    L[i][j] = math.sqrt(max(0, A[i][i] - s))
                else:
                    L[i][j] = (A[i][j] - s) / L[j][j] if L[j][j] > 0 else 0

        return L

    def _solve_triangular(self, L: List[List[float]], b: List[float]) -> List[float]:
        """Solve L @ x = b for lower triangular L."""
        n = len(b)
        x = [0.0] * n

        for i in range(n):
            s = sum(L[i][j] * x[j] for j in range(i))
            x[i] = (b[i] - s) / L[i][i] if L[i][i] > 0 else 0

        return x

    def _solve_triangular_transpose(
        self,
        L: List[List[float]],
        b: List[float]
    ) -> List[float]:
        """Solve L^T @ x = b for lower triangular L."""
        n = len(b)
        x = [0.0] * n

        for i in range(n - 1, -1, -1):
            s = sum(L[j][i] * x[j] for j in range(i + 1, n))
            x[i] = (b[i] - s) / L[i][i] if L[i][i] > 0 else 0

        return x

    def log_marginal_likelihood(self) -> float:
        """
        Compute log marginal likelihood of the training data.

        Used for hyperparameter optimization.
        """
        if self._X_train is None:
            return float('-inf')

        n = len(self._X_train)

        if HAS_NUMPY:
            # -0.5 * y^T @ K^{-1} @ y - 0.5 * log|K| - n/2 * log(2*pi)
            y = np.array(self._y_train)
            data_fit = -0.5 * float(y @ self._alpha)
            complexity = -np.sum(np.log(np.diag(self._L)))
            constant = -n / 2 * math.log(2 * math.pi)
            return data_fit + complexity + constant
        else:
            # Pure Python version
            data_fit = -0.5 * sum(
                self._y_train[i] * self._alpha[i] for i in range(n)
            )
            complexity = -sum(math.log(self._L[i][i]) for i in range(n))
            constant = -n / 2 * math.log(2 * math.pi)
            return data_fit + complexity + constant

    def sample_posterior(
        self,
        X: List[List[float]],
        n_samples: int = 1
    ) -> List[List[float]]:
        """
        Draw samples from the posterior distribution.

        Args:
            X: Points to sample at
            n_samples: Number of samples to draw

        Returns:
            List of n_samples, each is a list of values at X
        """
        if not HAS_NUMPY:
            raise RuntimeError("Posterior sampling requires numpy")

        means, stds = self.predict(X)
        means = np.array(means)
        stds = np.array(stds)

        # Draw samples: y = mean + std * z, z ~ N(0, 1)
        samples = []
        for _ in range(n_samples):
            z = np.random.randn(len(X))
            sample = means + stds * z
            samples.append(sample.tolist())

        return samples


class EnsembleGP:
    """
    Ensemble of Gaussian Processes for improved robustness.

    Combines predictions from multiple GPs with different kernels
    or hyperparameters.
    """

    def __init__(self, configs: List[GPConfig]):
        """
        Initialize ensemble.

        Args:
            configs: List of GP configurations
        """
        self.gps = [GaussianProcessSurrogate(config) for config in configs]
        self.weights = [1.0 / len(configs)] * len(configs)

    def fit(self, X: List[List[float]], y: List[float]) -> "EnsembleGP":
        """Fit all GPs to training data."""
        for gp in self.gps:
            gp.fit(X, y)

        # Update weights based on log marginal likelihood
        lmls = [gp.log_marginal_likelihood() for gp in self.gps]
        max_lml = max(lmls)

        # Softmax over log marginal likelihoods
        exp_lmls = [math.exp(lml - max_lml) for lml in lmls]
        total = sum(exp_lmls)
        self.weights = [e / total for e in exp_lmls]

        return self

    def predict(
        self,
        X: List[List[float]],
        return_std: bool = True
    ) -> Union[Tuple[List[float], List[float]], List[float]]:
        """
        Predict using weighted ensemble.

        Combines predictions using the mixture of experts approach.
        """
        all_means = []
        all_vars = []

        for gp in self.gps:
            means, stds = gp.predict(X, return_std=True)
            all_means.append(means)
            all_vars.append([s ** 2 for s in stds])

        # Weighted combination
        n = len(X)
        final_means = [0.0] * n
        final_vars = [0.0] * n

        for i in range(n):
            for j, w in enumerate(self.weights):
                final_means[i] += w * all_means[j][i]

            # Variance includes uncertainty about which GP is correct
            for j, w in enumerate(self.weights):
                final_vars[i] += w * (
                    all_vars[j][i] + (all_means[j][i] - final_means[i]) ** 2
                )

        final_stds = [math.sqrt(v) for v in final_vars]

        if return_std:
            return final_means, final_stds
        return final_means


if __name__ == "__main__":
    # Simple test
    print("Testing Gaussian Process Surrogate...")

    # Create synthetic data
    X_train = [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [0.5, 0.5]
    ]
    y_train = [0.0, 1.0, 1.0, 2.0, 1.2]  # Roughly f(x) = x1 + x2

    # Fit GP
    gp = GaussianProcessSurrogate()
    gp.fit(X_train, y_train)

    # Predict
    X_test = [[0.25, 0.25], [0.75, 0.75]]
    means, stds = gp.predict(X_test)

    print(f"Test points: {X_test}")
    print(f"Predicted means: {means}")
    print(f"Predicted stds: {stds}")
    print(f"Log marginal likelihood: {gp.log_marginal_likelihood():.4f}")

    # Test ensemble
    print("\nTesting Ensemble GP...")
    configs = [
        GPConfig(kernel=KernelType.RBF, length_scale=0.5),
        GPConfig(kernel=KernelType.RBF, length_scale=1.0),
        GPConfig(kernel=KernelType.MATERN_52, length_scale=1.0)
    ]
    ensemble = EnsembleGP(configs)
    ensemble.fit(X_train, y_train)

    means, stds = ensemble.predict(X_test)
    print(f"Ensemble weights: {ensemble.weights}")
    print(f"Ensemble predicted means: {means}")
    print(f"Ensemble predicted stds: {stds}")
