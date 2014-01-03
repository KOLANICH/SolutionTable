import numpy as np
import scipy as sp
import scipy.linalg
from matplotlib import pyplot as plt

from math import isclose


class Table:
	"""
	Tries to solve logical problems in Bayessian framework.
	!!! Doesn't work for now !!!
	"""

	__slots__ = ("axes", "tensor")

	def __init__(self, *labels):
		axCount = len(labels)
		labelsNew = []
		for ax in labels:
			ax = {l: i for i, l in enumerate(ax)}
			labelsNew.append(ax)
		labels = labelsNew

		self.axes = labels
		shape = tuple(len(lS) for lS in labels)
		self.tensor = self.getUniform(shape)
		self.axes = labels

	@property
	def shape(self):
		return self.tensor.shape[0]

	@classmethod
	def getUniform(cls, shape):
		"""Returns a Uniform distribution, normalized to 1 for **whole matrix**"""
		return np.ones(shape) * 1.0 / np.product(shape)  # * self.shape

	def iterMinor(self, i, j):
		"""Iterates over a matrix minor, yields INDICES"""
		for l in range(self.shape):
			for k in range(self.shape):
				if not (l == i or k == j):
					yield (l, k)

	def iterExcept(self, i, j):
		"""Iterates over all the els of a matrix, except the selected one"""
		for l in range(self.shape):
			for k in range(self.shape):
				if not (l == i and k == j):
					yield (l, k)

	def getMinor(self, i, j):
		"""Returns a minor as a matrix"""
		return np.delete(np.delete(self.tensor, i, axis=0), j, axis=1)

	def equal(self, a, b):
		"""Updates the posterior so that `a` maps to `b` with probability of 1."""
		i = self.axes[0][a]
		j = self.axes[1][b]
		self.bayesUpdate(self.getSingleElConditioned(1., i, j))

	def isNot(self, a, b):
		"""Updates the posterior so that `a` cannot map to `b` (in other words, maps to it with probability of `0`)."""
		i = self.axes[0][a]
		j = self.axes[1][b]
		self.bayesUpdate(self.getSingleElConditioned(0., i, j))

	def getSingleElConditioned(self, probability, i, j):
		"""Generates conditional distribution so that `a` cannot map to `b` (in other words, maps to it with probability of `0`)."""
		cond = np.zeros(self.tensor.shape)
		rowNorm = 1.0 / self.shape

		elNorm = probability * rowNorm

		restRowNorm = rowNorm - elNorm

		restRowEl = restRowNorm / (self.shape - 1)
		cond[i, :] = restRowEl
		cond[:, j] = restRowEl
		cond[i, j] = elNorm

		probabilityForTheMinorRow = rowNorm - restRowEl
		itemsInMinorRow = self.shape - 1
		minorRowEl = probabilityForTheMinorRow / itemsInMinorRow
		for el in self.iterMinor(i, j):
			cond[el] = minorRowEl


		plt.matshow(cond)
		plt.colorbar()
		plt.grid()
		plt.show()
		assert isclose(np.sum(cond), 1.), "Conditional probability distribution must normalize to 1 over whole matrix"

		return cond

	def plot(self):
		"""A convenience routine to plot the shit"""
		plt.matshow(self.tensor)
		plt.colorbar()
		plt.grid()
		plt.show()

	def bayesUpdate(self, cond):
		"""Updates the posterior in the tensor.
		(posterior := P(X|D)) * (margLik := P(D)) = (cond := P(D|X)) * (prior := P(X))
		"""
		prior = self.tensor

		#assert isclose(np.sum(prior), 1.), "Prior distribution must normalize to 1 over the whole matrix, but: " + str(np.sum(prior))

		joint_cond = prior * cond

		#elementNorm = 1. / self.shape / self.shape
		#assert isclose(np.sum(self.getUniform(prior.shape) - (prior + (elementNorm - prior))), 0.), "Uniform is the marginal prior"
		#margLik = self.getUniform(prior.shape) * cond  # getUniform() === (prior + (elementNorm - prior))

		#assert isclose(np.sum(margLik), 1.), "marginal likelyhood must normalize to 1 over the whole matrix, but: " + str(np.sum(margLik))
		#margLik = self.getUniform(prior.shape)
		rowNorm = 1. / self.shape
		elNorm = rowNorm / self.shape

		#plt.matshow(margLik)
		#plt.colorbar()
		#plt.grid()
		#plt.show()
		#posterior = np.zeros(joint_cond.shape)
		posterior = joint_cond

		# We need to replace this shit with something calculated analytically in a single step, and without using z3 or sympy or any other symbolic solver.
		# It is likely that to do it we just need to make all the marginals uniform (even if the product is not factored into marginals)
		# I guess it may be possible to express it in a form solving it via gaussian elimination. An eigenvector as a variant.
		
		for k in range(100):
			for i in range(self.shape):
				#for j in range(self.shape):
				#	if margLik[i, j]:
				#		posterior[i, j] = joint_cond[i, j] / margLik[i, j]
				#posterior[i] = joint_cond[i]


				# only alternating order works!
				currentRowNorm = np.sum(joint_cond[i])
				posterior[i] *= rowNorm / currentRowNorm

				#posterior[:, i] = joint_cond[:, i]
				currentCollNorm = np.sum(joint_cond[:, i])
				posterior[:, i] *= rowNorm / currentCollNorm

				#posterior[i] /= np.sum(posterior[i]) / self.shape
				#posterior[:, i] = joint_cond[:, i]
				#posterior[:, i] /= np.sum(posterior[:, i]) / self.shape

			

		plt.matshow(posterior)
		plt.colorbar()
		plt.grid()
		plt.show()

		#assert isclose(np.sum(posterior), 1.), "Posterior must normalize to 1 over the whole matrix, but: " + str(np.sum(posterior))

		self.tensor = posterior


def buildAlphaVec(a):
	"""A vector of "α" values.
	k is step of solution. k=0 is prior, k=1 is posterior got from prior with 1 conditional applied, k=2 - with 2 conditionals applied and so on.
	a_{l,(k+1)} = α(a_{l,(k)}) @ a_{l,(k+1)}   -- it is the result of resolution of the equation wrt a_{l,(k+1)}, where `l` is the equation number and
	α(a_{l,(k)}) := a_{l,(k)} / ( 1 - a_{l,(k)}/\\sum_{j}{a_{j,(k)}} )  -- the vector generated by this function"""

	alpha = np.zeros(len(a))
	norm = np.sum(a)
	for l in range(len(a)):
		#alpha[l] = 1 / (1 - a[l] / norm)
		alpha[l] = a[l] / norm
	return alpha


def buildBMat(old, coords):
	"""A matrix for an eigenvector-like problem for eigenvalue of 1. Need to solve it with Gaussian elimination.
	`coords	 is a try to exclude the row corresponding to the modified element from the matrix in order to prevent it from being relaxed, it must be rigid. Doesn't work for now."""
	alpha = buildAlphaVec(old)
	B = np.ones((len(old), len(old)))
	for i in range(len(old)):
		for j in range(len(old)):
			B[i, j] = alpha[i]
			if i == j:
				if coords is None or coords[0] != i:
					B[i, j] -= 1
				else:
					pass

	return B


def computeNewShit(a, coords=None):
	"""Tries to relax a vector with elements modified to a new value satisfying the normalization to 1."""

	B = buildBMat(a, coords)  # det B === 0
	#return scipy.linalg.solve(B, np.zeros(len(a)))

	if coords is not None:
		coord2ReplaceWithNormN = coords[0]
	else:
		coord2ReplaceWithNormN = -1

	#replace the last row with normalization
	for i in range(len(a)):
		B[coord2ReplaceWithNormN, i] = 1.0

	if coords is not None:
		B[coords[0], coords[0]] = 0.0

	rhs = np.zeros(len(a))
	if coords is not None:
		rhs[coord2ReplaceWithNormN] = 1.0 - a[coords]
	else:
		rhs[coord2ReplaceWithNormN] = 1.0

	return np.linalg.solve(B, rhs)
