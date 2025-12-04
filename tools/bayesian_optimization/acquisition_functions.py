#!/usr/bin/env python3
"""
Acquisition Functions for Bayesian Architecture Optimization

Acquisition functions guide the search for optimal architectures by balancing
exploration (trying uncertain regions) and exploitation (optimizing in
promising regions).

Available Functions:
- Expected Improvement (EI): Most popular, balances exploration/exploitation
- Upper Confidence Bound (UCB): Tunable exploration via kappa parameter
- Probability of Improvement (PI): Conservative, focuses on improvement
- Thompson Sampling: Draws samples from posterior, naturally explores
- Knowledge Gradient: Considers value of information

Usage:
    from acquisition_functions import expected_improvement, upper_confidence_bound

    # Get GP predictions
    means, stds = gp.predict(candidates)

    # Compute acquisition values
    ei_values = expected_improvement(means, stds, best_so_far)
    ucb_values = upper_confidence_bound(means, stds, kappa=2.0)

    # Select candidate with highest acquisition value
    best_idx = max(range(len(ei_values)), key=lambda i: ei_values[i])

Version: 0.1.0
"""

import math
from typing import List, Tuple, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class AcquisitionType(Enum):
    """Available acquisition functions."""
    EXPECTED_IMPROVEMENT = "ei"
    UPPER_CONFIDENCE_BOUND = "ucb"
    LOWER_CONFIDENCE_BOUND = "lcb"  # For minimization
    PROBABILITY_OF_IMPROVEMENT = "pi"
    THOMPSON_SAMPLING = "ts"
    KNOWLEDGE_GRADIENT = "kg"


@dataclass
class AcquisitionConfig:
    """Configuration for acquisition function."""
    acquisition_type: AcquisitionType = AcquisitionType.EXPECTED_IMPROVEMENT
    kappa: float = 2.0  # UCB/LCB exploration parameter
    xi: float = 0.01  # EI/PI exploration parameter
    minimize: bool = True  # Whether minimizing (True) or maximizing (False)


# Standard normal CDF and PDF

def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


# Core acquisition functions

def expected_improvement(
    means: List[float],
    stds: List[float],
    best_so_far: float,
    xi: float = 0.01,
    minimize: bool = True
) -> List[float]:
    """
    Expected Improvement (EI) acquisition function.

    EI measures the expected amount of improvement over the current best.
    It naturally balances exploration (high uncertainty) and exploitation
    (predicted to be good).

    For minimization:
        EI(x) = E[max(0, f_best - f(x))]
             = (f_best - mu - xi) * Phi(Z) + sigma * phi(Z)
        where Z = (f_best - mu - xi) / sigma

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        best_so_far: Best objective value observed so far
        xi: Exploration parameter (larger = more exploration)
        minimize: True for minimization, False for maximization

    Returns:
        List of EI values for each candidate
    """
    ei_values = []

    for mu, sigma in zip(means, stds):
        if sigma <= 0:
            ei_values.append(0.0)
            continue

        if minimize:
            improvement = best_so_far - mu - xi
        else:
            improvement = mu - best_so_far - xi

        z = improvement / sigma

        # EI = improvement * Phi(z) + sigma * phi(z)
        ei = improvement * _norm_cdf(z) + sigma * _norm_pdf(z)
        ei_values.append(max(0, ei))

    return ei_values


def upper_confidence_bound(
    means: List[float],
    stds: List[float],
    kappa: float = 2.0
) -> List[float]:
    """
    Upper Confidence Bound (UCB) acquisition function.

    UCB provides an optimistic estimate of the objective value.
    Higher kappa means more exploration.

    UCB(x) = mu(x) + kappa * sigma(x)

    Use for MAXIMIZATION problems. For minimization, use lower_confidence_bound.

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        kappa: Exploration parameter (typically 1.0-3.0)

    Returns:
        List of UCB values (higher is better for selection)
    """
    return [mu + kappa * sigma for mu, sigma in zip(means, stds)]


def lower_confidence_bound(
    means: List[float],
    stds: List[float],
    kappa: float = 2.0
) -> List[float]:
    """
    Lower Confidence Bound (LCB) acquisition function.

    The minimization counterpart to UCB.

    LCB(x) = mu(x) - kappa * sigma(x)

    Use for MINIMIZATION problems. Select the candidate with LOWEST LCB.

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        kappa: Exploration parameter (typically 1.0-3.0)

    Returns:
        List of LCB values (LOWER is better for selection)
    """
    return [mu - kappa * sigma for mu, sigma in zip(means, stds)]


def probability_of_improvement(
    means: List[float],
    stds: List[float],
    best_so_far: float,
    xi: float = 0.01,
    minimize: bool = True
) -> List[float]:
    """
    Probability of Improvement (PI) acquisition function.

    PI measures the probability of finding a value better than the current best.
    More conservative than EI (doesn't consider magnitude of improvement).

    For minimization:
        PI(x) = Phi((f_best - mu - xi) / sigma)

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        best_so_far: Best objective value observed so far
        xi: Exploration parameter (larger = require bigger improvement)
        minimize: True for minimization, False for maximization

    Returns:
        List of PI values (probability in [0, 1])
    """
    pi_values = []

    for mu, sigma in zip(means, stds):
        if sigma <= 0:
            # No uncertainty - check if predicted to be better
            if minimize:
                pi_values.append(1.0 if mu < best_so_far - xi else 0.0)
            else:
                pi_values.append(1.0 if mu > best_so_far + xi else 0.0)
            continue

        if minimize:
            z = (best_so_far - mu - xi) / sigma
        else:
            z = (mu - best_so_far - xi) / sigma

        pi_values.append(_norm_cdf(z))

    return pi_values


def thompson_sampling(
    means: List[float],
    stds: List[float],
    n_samples: int = 1,
    minimize: bool = True
) -> List[int]:
    """
    Thompson Sampling acquisition.

    Draws samples from the posterior and selects based on samples.
    Naturally handles exploration via posterior sampling.

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        n_samples: Number of samples to draw (returns indices for each)
        minimize: True for minimization, False for maximization

    Returns:
        List of indices of selected candidates (one per sample)
    """
    import random

    selected = []

    for _ in range(n_samples):
        # Draw samples from posterior at each candidate
        samples = [
            random.gauss(mu, sigma) for mu, sigma in zip(means, stds)
        ]

        # Select best sample
        if minimize:
            best_idx = min(range(len(samples)), key=lambda i: samples[i])
        else:
            best_idx = max(range(len(samples)), key=lambda i: samples[i])

        selected.append(best_idx)

    return selected


def knowledge_gradient(
    means: List[float],
    stds: List[float],
    noise_var: float = 1e-6,
    minimize: bool = True
) -> List[float]:
    """
    Knowledge Gradient (KG) acquisition function.

    Measures the expected improvement in the posterior minimum (or maximum)
    after observing the candidate point. More computationally expensive
    but can be more sample-efficient.

    Approximate KG via one-step lookahead.

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        noise_var: Observation noise variance
        minimize: True for minimization, False for maximization

    Returns:
        List of KG values
    """
    kg_values = []

    current_best_mean = min(means) if minimize else max(means)

    for i, (mu, sigma) in enumerate(zip(means, stds)):
        if sigma <= 0:
            kg_values.append(0.0)
            continue

        # Posterior predictive std after observing this point
        # sigma_post = sqrt(sigma^2 * noise_var / (sigma^2 + noise_var))
        sigma_sq = sigma ** 2
        sigma_post = math.sqrt(sigma_sq * noise_var / (sigma_sq + noise_var))

        # Expected improvement in posterior mean at this point
        # approximation: improvement from uncertainty reduction
        if minimize:
            improvement = current_best_mean - mu
        else:
            improvement = mu - current_best_mean

        z = improvement / sigma if sigma > 0 else 0

        # KG ≈ sigma * (z * Phi(z) + phi(z))
        kg = sigma * (z * _norm_cdf(z) + _norm_pdf(z))
        kg_values.append(max(0, kg))

    return kg_values


# Composite acquisition functions

def portfolio_acquisition(
    means: List[float],
    stds: List[float],
    best_so_far: float,
    weights: Optional[dict] = None,
    minimize: bool = True
) -> List[float]:
    """
    Portfolio acquisition combining multiple acquisition functions.

    Useful when uncertain about which acquisition function to use.

    Args:
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        best_so_far: Best objective value observed so far
        weights: Dict of {acquisition_type: weight}, defaults to equal weights
        minimize: True for minimization, False for maximization

    Returns:
        List of combined acquisition values
    """
    if weights is None:
        weights = {
            "ei": 0.4,
            "ucb": 0.3,
            "pi": 0.3
        }

    n = len(means)
    combined = [0.0] * n

    if "ei" in weights:
        ei = expected_improvement(means, stds, best_so_far, minimize=minimize)
        # Normalize EI to [0, 1]
        max_ei = max(ei) if max(ei) > 0 else 1.0
        ei_norm = [e / max_ei for e in ei]
        for i in range(n):
            combined[i] += weights["ei"] * ei_norm[i]

    if "ucb" in weights or "lcb" in weights:
        if minimize:
            # For minimization, negate LCB (lower is better)
            lcb = lower_confidence_bound(means, stds)
            min_lcb, max_lcb = min(lcb), max(lcb)
            range_lcb = max_lcb - min_lcb if max_lcb > min_lcb else 1.0
            lcb_norm = [(max_lcb - l) / range_lcb for l in lcb]  # Invert for selection
            w = weights.get("lcb", weights.get("ucb", 0.3))
            for i in range(n):
                combined[i] += w * lcb_norm[i]
        else:
            ucb = upper_confidence_bound(means, stds)
            min_ucb, max_ucb = min(ucb), max(ucb)
            range_ucb = max_ucb - min_ucb if max_ucb > min_ucb else 1.0
            ucb_norm = [(u - min_ucb) / range_ucb for u in ucb]
            w = weights.get("ucb", 0.3)
            for i in range(n):
                combined[i] += w * ucb_norm[i]

    if "pi" in weights:
        pi = probability_of_improvement(means, stds, best_so_far, minimize=minimize)
        for i in range(n):
            combined[i] += weights["pi"] * pi[i]

    return combined


# Selection utilities

def select_next(
    candidates: List[List[float]],
    acquisition_values: List[float],
    n_select: int = 1,
    exclude_indices: Optional[List[int]] = None,
    maximize: bool = True
) -> List[int]:
    """
    Select next candidate(s) based on acquisition values.

    Args:
        candidates: List of candidate feature vectors
        acquisition_values: Acquisition values for each candidate
        n_select: Number of candidates to select
        exclude_indices: Indices to exclude from selection
        maximize: Whether higher acquisition is better (True for most)

    Returns:
        List of selected indices
    """
    exclude = set(exclude_indices or [])

    # Create (index, value) pairs excluding already evaluated
    indexed = [
        (i, v) for i, v in enumerate(acquisition_values)
        if i not in exclude
    ]

    # Sort by value
    indexed.sort(key=lambda x: x[1], reverse=maximize)

    # Return top n_select indices
    return [idx for idx, _ in indexed[:n_select]]


def batch_select(
    candidates: List[List[float]],
    means: List[float],
    stds: List[float],
    best_so_far: float,
    n_select: int = 5,
    acquisition_type: AcquisitionType = AcquisitionType.EXPECTED_IMPROVEMENT,
    minimize: bool = True,
    diversity_weight: float = 0.1
) -> List[int]:
    """
    Select a batch of diverse candidates for parallel evaluation.

    Uses local penalization to encourage diversity in the batch.

    Args:
        candidates: List of candidate feature vectors
        means: Predicted means from GP
        stds: Predicted standard deviations from GP
        best_so_far: Best objective value observed so far
        n_select: Batch size
        acquisition_type: Which acquisition function to use
        minimize: True for minimization
        diversity_weight: How much to penalize similarity to selected

    Returns:
        List of selected indices
    """
    # Compute base acquisition values
    if acquisition_type == AcquisitionType.EXPECTED_IMPROVEMENT:
        acq_values = expected_improvement(means, stds, best_so_far, minimize=minimize)
    elif acquisition_type == AcquisitionType.UPPER_CONFIDENCE_BOUND:
        if minimize:
            acq_values = [-v for v in lower_confidence_bound(means, stds)]
        else:
            acq_values = upper_confidence_bound(means, stds)
    elif acquisition_type == AcquisitionType.PROBABILITY_OF_IMPROVEMENT:
        acq_values = probability_of_improvement(means, stds, best_so_far, minimize=minimize)
    else:
        acq_values = expected_improvement(means, stds, best_so_far, minimize=minimize)

    selected = []
    remaining_acq = acq_values.copy()

    for _ in range(n_select):
        # Select best remaining
        best_idx = max(range(len(remaining_acq)), key=lambda i: remaining_acq[i])
        selected.append(best_idx)

        if len(selected) >= n_select:
            break

        # Penalize similar candidates
        selected_candidate = candidates[best_idx]

        for i in range(len(candidates)):
            if i in selected:
                remaining_acq[i] = float('-inf')
                continue

            # Compute distance to selected
            dist = math.sqrt(sum(
                (a - b) ** 2
                for a, b in zip(candidates[i], selected_candidate)
            ))

            # Local penalization
            penalty = diversity_weight * math.exp(-0.5 * dist)
            remaining_acq[i] *= (1 - penalty)

    return selected


class AcquisitionOptimizer:
    """
    Wrapper class for acquisition function optimization.

    Provides a unified interface for computing acquisition values
    and selecting candidates.
    """

    def __init__(self, config: Optional[AcquisitionConfig] = None):
        """
        Initialize acquisition optimizer.

        Args:
            config: Acquisition configuration
        """
        self.config = config or AcquisitionConfig()

    def compute(
        self,
        means: List[float],
        stds: List[float],
        best_so_far: float
    ) -> List[float]:
        """
        Compute acquisition values.

        Args:
            means: Predicted means
            stds: Predicted standard deviations
            best_so_far: Best observed value

        Returns:
            Acquisition values for each candidate
        """
        if self.config.acquisition_type == AcquisitionType.EXPECTED_IMPROVEMENT:
            return expected_improvement(
                means, stds, best_so_far,
                xi=self.config.xi,
                minimize=self.config.minimize
            )

        elif self.config.acquisition_type == AcquisitionType.UPPER_CONFIDENCE_BOUND:
            return upper_confidence_bound(means, stds, kappa=self.config.kappa)

        elif self.config.acquisition_type == AcquisitionType.LOWER_CONFIDENCE_BOUND:
            return lower_confidence_bound(means, stds, kappa=self.config.kappa)

        elif self.config.acquisition_type == AcquisitionType.PROBABILITY_OF_IMPROVEMENT:
            return probability_of_improvement(
                means, stds, best_so_far,
                xi=self.config.xi,
                minimize=self.config.minimize
            )

        elif self.config.acquisition_type == AcquisitionType.KNOWLEDGE_GRADIENT:
            return knowledge_gradient(means, stds, minimize=self.config.minimize)

        else:
            return expected_improvement(means, stds, best_so_far, minimize=self.config.minimize)

    def select(
        self,
        candidates: List[List[float]],
        means: List[float],
        stds: List[float],
        best_so_far: float,
        n_select: int = 1,
        exclude_indices: Optional[List[int]] = None
    ) -> List[int]:
        """
        Select next candidate(s) to evaluate.

        Args:
            candidates: Candidate feature vectors
            means: Predicted means
            stds: Predicted standard deviations
            best_so_far: Best observed value
            n_select: Number to select
            exclude_indices: Indices to exclude

        Returns:
            Indices of selected candidates
        """
        if self.config.acquisition_type == AcquisitionType.THOMPSON_SAMPLING:
            return thompson_sampling(
                means, stds,
                n_samples=n_select,
                minimize=self.config.minimize
            )

        acq_values = self.compute(means, stds, best_so_far)

        # For LCB, we want minimum not maximum
        maximize = self.config.acquisition_type != AcquisitionType.LOWER_CONFIDENCE_BOUND

        return select_next(
            candidates, acq_values,
            n_select=n_select,
            exclude_indices=exclude_indices,
            maximize=maximize
        )


if __name__ == "__main__":
    # Simple test
    print("Testing Acquisition Functions...")

    # Mock GP predictions
    means = [1.0, 0.8, 1.2, 0.5, 0.9]
    stds = [0.3, 0.5, 0.2, 0.4, 0.1]
    best_so_far = 0.6  # Current best (minimizing)

    print(f"\nMeans: {means}")
    print(f"Stds: {stds}")
    print(f"Best so far: {best_so_far}")

    # Test each acquisition function
    print("\nExpected Improvement (minimize):")
    ei = expected_improvement(means, stds, best_so_far, minimize=True)
    print(f"  EI: {[f'{v:.4f}' for v in ei]}")
    print(f"  Best idx: {max(range(len(ei)), key=lambda i: ei[i])}")

    print("\nLower Confidence Bound:")
    lcb = lower_confidence_bound(means, stds, kappa=2.0)
    print(f"  LCB: {[f'{v:.4f}' for v in lcb]}")
    print(f"  Best idx: {min(range(len(lcb)), key=lambda i: lcb[i])}")

    print("\nProbability of Improvement (minimize):")
    pi = probability_of_improvement(means, stds, best_so_far, minimize=True)
    print(f"  PI: {[f'{v:.4f}' for v in pi]}")
    print(f"  Best idx: {max(range(len(pi)), key=lambda i: pi[i])}")

    print("\nKnowledge Gradient:")
    kg = knowledge_gradient(means, stds, minimize=True)
    print(f"  KG: {[f'{v:.4f}' for v in kg]}")
    print(f"  Best idx: {max(range(len(kg)), key=lambda i: kg[i])}")

    print("\nPortfolio Acquisition:")
    portfolio = portfolio_acquisition(means, stds, best_so_far, minimize=True)
    print(f"  Portfolio: {[f'{v:.4f}' for v in portfolio]}")
    print(f"  Best idx: {max(range(len(portfolio)), key=lambda i: portfolio[i])}")

    print("\nBatch Selection (3 diverse candidates):")
    candidates = [[i, i*0.5] for i in range(5)]  # Mock feature vectors
    batch = batch_select(
        candidates, means, stds, best_so_far,
        n_select=3, minimize=True
    )
    print(f"  Selected indices: {batch}")
