import configparser
import typing
from collections import OrderedDict
from pathlib import Path

"""This module parses .prb files used in "Delphi for Fun" [Logic Problem Solver](http://delphiforfun.org/Programs/logic_problem_solver.htm) by Gary Darby.
These are ini files containing semi-formal description of some class of school-level logical problems that can be solved by using tables.
"""


def arrayizeDict(g):
	"""Transforms a dict with unique sequential integer indices into an array"""
	mk = max(g.keys())
	ga = [None] * mk
	for k, v in g.items():
		ga[k - 1] = v
	return ga


def arrayize(pp):
	"""Transforms the dicts with unique sequential integer indices into an array"""
	for sk, s in pp.items():
		for gk in tuple(s.keys()):
			s[gk] = arrayizeDict(s[gk])


def preliminaryParse(t):
	"""Parses a prb file text (which is based on ini) into a hierarchy of dicts and """

	c = configparser.ConfigParser()
	c.read_string(t)

	res = {}
	for sN in c.sections():
		sNl = sN.lower()
		dGroups = schema[sNl].GROUPS
		s = c[sN]
		res[sNl] = secParsed = {}

		for k, v in s.items():
			k = k.lower()
			g = None
			for gN in dGroups:
				if k.startswith(gN):
					g = secParsed.get(gN, None)
					if g is None:
						secParsed[gN] = g = {}
					k = int(k[len(gN) :])
					break
			g[k] = v

	arrayize(res)
	return res


class PRBInfoSection:
	__slots__ = ()

	NAME = None
	GROUPS = None

	@classmethod
	def csv(cls, lines):
		for v in lines:
			if v is not None:
				yield v.split(",")


class Dimension:
	__slots__ = ("idx", "name", "entities", "connectWords")

	def __init__(self, idx, name, entities):
		self.idx = idx
		self.name = name
		self.entities = {}
		self.connectWords = {}
		for el in entities:
			self.entities[el] = Entity(el, self)

	def get(self, v):
		return self.entities.get(v, None)


class Entity:
	__slots__ = ("id", "dimension")

	def __init__(self, iD, dimension):
		self.id = iD
		self.dimension = dimension

	def toTuple(self):
		return (self.dimension.name, self.id)

	def __hash__(self):
		return hash(self.toTuple())

	def __id__(self):
		return id(self.toTuple())

	def __eq__(self, other):
		return isinstance(other, __class__) and self.toTuple() == other.toTuple()

	def __str__(self):
		return ".".join(self.toTuple())


paragraphNoSpecialValues = {"None", ''}

def parseParagraphNo(s):
	if s in paragraphNoSpecialValues:
		return None

	return int(s)


class Fact:
	__slots__ = ("paragraphNo", "entities", "isEnabled")

	SYMBOL = None

	def __init__(self, paragraphNo, entities, isEnabled):
		self.paragraphNo = paragraphNo
		self.entities = entities
		self.isEnabled = isEnabled

	def __str__(self):
		return (" " + self.__class__.SYMBOL + " ").join(str(el) for el in self.entities)


class RangeFact(Fact):
	"""Used to specify that
		* entities of that kind are ordered and is in range. Ordering is unknown and doesn't correspond to the ordering of vars;
		* That an entity is at specific distance from another entity.
	"""

	__slots__ = ("dimension", "isThisTrue", "amount")

	SYMBOL = ">"

	def __init__(self, paragraphNo, entities, isEnabled, isThisTrue, dimension, amount):
		super().__init__(paragraphNo, entities, isEnabled)
		self.dimension = dimension
		self.isThisTrue = isThisTrue
		self.amount = amount

	@classmethod
	def fromIniValue(cls, description, v):
		paragraphNo = v[1]
		paragraphNo = parseParagraphNo(paragraphNo)

		entities = (description.searchValue(v[2]), description.searchValue(v[4]))

		relation = v[3]

		dimensionName = v[5]
		dimension = description.dims[dimensionName]

		orderId = v[0]
		amount = v[6]
		if amount == "Unknown":
			amount = float("nan")
		else:
			amount = int(amount)

		isThisTrue = v[7]
		isThisTrue = isThisTrue == "T"
		if len(v) > 8:
			isEnabled = v[8]  # usually "X"
		else:
			isEnabled = True

		return orderingRelationsMapping[relation](paragraphNo, entities, isEnabled, isThisTrue, dimension, amount)


class DistanceConstraintFact(RangeFact):
	__slots__ = ()

	SYMBOL = "-"

	def __init__(self, paragraphNo, entities, isEnabled, isThisTrue, dimension, amount):
		super().__init__(paragraphNo, entities, isEnabled, isThisTrue, dimension, amount)
		self.dimension = dimension

	def __str__(self):
		return super().__str__() + (" == " + str(self.amount) if self.amount is not None else "")


def beforeFactCtor(*args):
	f = RangeFact(*args)
	f.entities = tuple(reversed(f.entities))
	f.amount = -f.amount
	return f


orderingRelationsMapping = {"After": RangeFact, "Before": beforeFactCtor, "Separated by": DistanceConstraintFact}


class MappingFact(Fact):
	__slots__ = ()

	@property
	def isMaps(self) -> bool:
		raise NotImplementedError

	@classmethod
	def fromIniValue(cls, description, valueResTuple):
		paragraphNo = valueResTuple[0]
		paragraphNo = parseParagraphNo(paragraphNo)
		entities = tuple(sorted((description.searchValue(e) for e in valueResTuple[1:3]), key=lambda e: e.dimension.idx))
		mapsOrNot = valueResTuple[3] == "True"
		if len(valueResTuple) > 5:
			isEnabled = valueResTuple[4]  # usually "X"
		else:
			isEnabled = True

		return mapsOrNotMapping[mapsOrNot](paragraphNo, entities, isEnabled)


class MapsFact(MappingFact):
	__slots__ = ()
	SYMBOL = "<=>"

	def isMaps(self):
		return True


class NotMapsFact(MappingFact):
	__slots__ = ()
	SYMBOL = "<!=>"

	def isMaps(self):
		return False


mapsOrNotMapping = {
	True: MapsFact,
	False: NotMapsFact
}


class SolutionSection(PRBInfoSection):
	__slots__ = ("ifRules", "choicesStatements", "orderFacts", "mappingFacts")

	NAME = "orig"
	GROUPS = ("stmt", "sep", "ifrule", "choicestmt")

	def __init__(self, description, preliminaryParsed):
		super().__init__()

		self.ifRules = []
		self.choicesStatements = []
		self.orderFacts = []
		self.mappingFacts = []

		for v in self.__class__.csv(preliminaryParsed.get("stmt", ())):
			self.mappingFacts.append(MappingFact.fromIniValue(description, v))

		for v in self.__class__.csv(preliminaryParsed.get("sep", ())):
			r = RangeFact.fromIniValue(description, v)
			self.orderFacts.append(r)

		for v in self.__class__.csv(preliminaryParsed.get("ifrule", ())):
			self.ifRules.append(v)

		for v in self.__class__.csv(preliminaryParsed.get("choicestmt", ())):
			self.choicesStatements.append(v)


class DescriptionSection(PRBInfoSection):
	__slots__ = ("text", "dims", "source")

	NAME = "description"
	GROUPS = ("text", "var", "source", "connectword")

	def __init__(self, preliminaryParsed):
		super().__init__()
		self.dims = OrderedDict()

		self.source = None
		s = preliminaryParsed.get("source", None)
		if s:
			self.source = "\n".join(s)
		self.text = "\n".join(preliminaryParsed["text"])

		for idx, vs in enumerate(self.__class__.csv(preliminaryParsed.get("var", ()))):
			name = vs[0]
			vs = vs[1:]
			self.dims[name] = Dimension(idx, name, vs)

		for dim1Name, maps, unmaps, dim2Name in self.__class__.csv(preliminaryParsed.get("connectword", ())):
			if dim1Name and dim2Name and maps and unmaps:
				self.dims[dim1Name].connectWords[dim2Name] = (unmaps, maps)

	def searchValue(self, v):
		for dim in self.dims.values():
			res = dim.get(v)
			if res:
				return res


schema = {"description": DescriptionSection, "orig": SolutionSection, "user": SolutionSection}


class PRB:
	__slots__ = ("orig", "description", "user")

	def __init__(self, src: typing.Union[str, Path, dict]):
		self.orig = None
		self.user = None

		if isinstance(src, Path):
			src = src.read_text(encoding="cp1252")

		if isinstance(src, str):
			src = preliminaryParse(src)

		self.description = DescriptionSection(src["description"])
		
		o = src.get("orig", None)
		if o:
			self.orig = SolutionSection(self.description, o)

		u = src.get("user", None)
		if u:
			self.user = SolutionSection(self.description, u)
