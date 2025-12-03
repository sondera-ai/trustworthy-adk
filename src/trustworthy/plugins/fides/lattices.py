"""
Lattice-based Security Labels for Information Flow Control

This module implements the mathematical lattice structures used in Fides for
representing and manipulating security labels. Based on the formal model
presented in "Securing AI Agents with Information-Flow Control".

Key Components:
- Abstract Lattice base class with join, meet, and ordering operations
- IntegrityLabel for trusted/untrusted classification
- PowersetLattice for confidentiality labels based on sets
- ProductLabel for combining multiple lattice dimensions
- InverseLattice for dual lattice structures
"""

from abc import ABC, abstractmethod
from typing import Any, FrozenSet, Generic, TypeVar, Union
from functools import reduce


class Lattice(ABC):
    """
    Abstract base class for security lattices.
    
    A lattice is a partially ordered set where every pair of elements has
    a unique least upper bound (join) and greatest lower bound (meet).
    
    Security labels form lattices where:
    - Join (∨) represents the least restrictive combination of labels
    - Meet (∧) represents the most restrictive combination of labels
    - Ordering (≤) represents the "can flow to" relation
    """

    @abstractmethod
    def leq(self, other: "Lattice") -> bool:
        """
        Check if this label can flow to another label (≤ relation).
        
        Args:
            other: The target label to check flow to
            
        Returns:
            True if information can flow from self to other
        """
        pass

    @abstractmethod
    def join(self, other: "Lattice") -> "Lattice":
        """
        Compute the least upper bound (join) of two labels.
        
        The join represents the least restrictive label that is at least
        as restrictive as both input labels.
        
        Args:
            other: The other label to join with
            
        Returns:
            The joined label
        """
        pass

    @abstractmethod
    def meet(self, other: "Lattice") -> "Lattice":
        """
        Compute the greatest lower bound (meet) of two labels.
        
        The meet represents the most restrictive label that is at most
        as restrictive as both input labels.
        
        Args:
            other: The other label to meet with
            
        Returns:
            The meet label
        """
        pass

    def __le__(self, other: "Lattice") -> bool:
        """Convenience method for ≤ relation."""
        return self.leq(other)

    def __or__(self, other: "Lattice") -> "Lattice":
        """Convenience method for join operation (|)."""
        return self.join(other)

    def __and__(self, other: "Lattice") -> "Lattice":
        """Convenience method for meet operation (&)."""
        return self.meet(other)


class IntegrityLabel(Lattice):
    """
    Two-point lattice for integrity labels: TRUSTED ≤ UNTRUSTED.
    
    This represents the standard integrity lattice where:
    - TRUSTED: Information from trusted sources
    - UNTRUSTED: Information from untrusted sources
    
    Information can flow from TRUSTED to UNTRUSTED but not vice versa.
    This prevents untrusted data from influencing trusted computations.
    """

    def __init__(self, is_trusted: bool):
        """
        Initialize an integrity label.
        
        Args:
            is_trusted: True for TRUSTED, False for UNTRUSTED
        """
        self.is_trusted = is_trusted

    @classmethod
    def trusted(cls) -> "IntegrityLabel":
        """Create a TRUSTED integrity label."""
        return cls(True)

    @classmethod
    def untrusted(cls) -> "IntegrityLabel":
        """Create an UNTRUSTED integrity label."""
        return cls(False)

    def leq(self, other: "IntegrityLabel") -> bool:
        """TRUSTED ≤ UNTRUSTED, TRUSTED ≤ TRUSTED, UNTRUSTED ≤ UNTRUSTED."""
        if not isinstance(other, IntegrityLabel):
            return False
        return self.is_trusted or not other.is_trusted

    def join(self, other: "IntegrityLabel") -> "IntegrityLabel":
        """Join: TRUSTED ∨ UNTRUSTED = UNTRUSTED."""
        if not isinstance(other, IntegrityLabel):
            raise TypeError("Can only join with another IntegrityLabel")
        return IntegrityLabel(self.is_trusted and other.is_trusted)

    def meet(self, other: "IntegrityLabel") -> "IntegrityLabel":
        """Meet: TRUSTED ∧ UNTRUSTED = TRUSTED."""
        if not isinstance(other, IntegrityLabel):
            raise TypeError("Can only meet with another IntegrityLabel")
        return IntegrityLabel(self.is_trusted or other.is_trusted)

    def __repr__(self) -> str:
        return "TRUSTED" if self.is_trusted else "UNTRUSTED"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, IntegrityLabel) and self.is_trusted == other.is_trusted

    def __hash__(self) -> int:
        return hash(self.is_trusted)


T = TypeVar('T')


class PowersetLattice(Lattice, Generic[T]):
    """
    Powerset lattice for confidentiality labels.
    
    This lattice represents sets of principals (e.g., email addresses, user IDs)
    who are allowed to see the information. The ordering is subset inclusion:
    smaller sets are more restrictive (higher confidentiality).
    
    Example: {alice} ≤ {alice, bob} means information visible to alice
    can flow to information visible to both alice and bob.
    """

    def __init__(self, subset: FrozenSet[T], universe: FrozenSet[T]):
        """
        Initialize a powerset lattice element.
        
        Args:
            subset: The set of principals who can access this information
            universe: The universe of all possible principals
        """
        if not subset.issubset(universe):
            raise ValueError("Subset must be contained in universe")
        self.subset = subset
        self.universe = universe

    def leq(self, other: "PowersetLattice[T]") -> bool:
        """Subset inclusion: self ≤ other iff self.subset ⊆ other.subset."""
        if not isinstance(other, PowersetLattice):
            return False
        return self.subset.issubset(other.subset)

    def join(self, other: "PowersetLattice[T]") -> "PowersetLattice[T]":
        """Join: union of subsets (less restrictive)."""
        if not isinstance(other, PowersetLattice):
            raise TypeError("Can only join with another PowersetLattice")
        return PowersetLattice(self.subset.union(other.subset), self.universe)

    def meet(self, other: "PowersetLattice[T]") -> "PowersetLattice[T]":
        """Meet: intersection of subsets (more restrictive)."""
        if not isinstance(other, PowersetLattice):
            raise TypeError("Can only meet with another PowersetLattice")
        return PowersetLattice(self.subset.intersection(other.subset), self.universe)

    def __repr__(self) -> str:
        return f"Powerset({{{', '.join(map(str, self.subset))}}})"

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, PowersetLattice) and 
                self.subset == other.subset and 
                self.universe == other.universe)

    def __hash__(self) -> int:
        return hash((self.subset, self.universe))

    @classmethod
    def bottom(cls, universe: FrozenSet[T]) -> "PowersetLattice[T]":
        """Create the bottom element (empty set - most restrictive)."""
        return cls(frozenset(), universe)

    @classmethod
    def top(cls, universe: FrozenSet[T]) -> "PowersetLattice[T]":
        """Create the top element (full universe - least restrictive)."""
        return cls(universe, universe)


L1 = TypeVar('L1', bound=Lattice)
L2 = TypeVar('L2', bound=Lattice)


class ProductLabel(Lattice, Generic[L1, L2]):
    """
    Product lattice combining two lattice dimensions.
    
    This allows combining different types of security labels, such as
    integrity and confidentiality. The ordering is component-wise:
    (a1, b1) ≤ (a2, b2) iff a1 ≤ a2 and b1 ≤ b2.
    
    Example: (TRUSTED, {alice}) ≤ (UNTRUSTED, {alice, bob})
    """

    def __init__(self, left: L1, right: L2):
        """
        Initialize a product label.
        
        Args:
            left: The left component label
            right: The right component label
        """
        self.left = left
        self.right = right

    def leq(self, other: "ProductLabel[L1, L2]") -> bool:
        """Component-wise ordering."""
        if not isinstance(other, ProductLabel):
            return False
        return self.left <= other.left and self.right <= other.right

    def join(self, other: "ProductLabel[L1, L2]") -> "ProductLabel[L1, L2]":
        """Component-wise join."""
        if not isinstance(other, ProductLabel):
            raise TypeError("Can only join with another ProductLabel")
        return ProductLabel(self.left.join(other.left), self.right.join(other.right))

    def meet(self, other: "ProductLabel[L1, L2]") -> "ProductLabel[L1, L2]":
        """Component-wise meet."""
        if not isinstance(other, ProductLabel):
            raise TypeError("Can only meet with another ProductLabel")
        return ProductLabel(self.left.meet(other.left), self.right.meet(other.right))

    def __repr__(self) -> str:
        return f"({self.left}, {self.right})"

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, ProductLabel) and 
                self.left == other.left and 
                self.right == other.right)

    def __hash__(self) -> int:
        return hash((self.left, self.right))


L = TypeVar('L', bound=Lattice)


class InverseLattice(Lattice, Generic[L]):
    """
    Inverse (dual) of a lattice.
    
    This reverses the ordering of the underlying lattice:
    - If a ≤ b in the original lattice, then Inverse(b) ≤ Inverse(a)
    - Join and meet operations are swapped
    
    This is useful for confidentiality labels where smaller sets should
    be "higher" in the security ordering.
    """

    def __init__(self, inner: L):
        """
        Initialize an inverse lattice element.
        
        Args:
            inner: The underlying lattice element
        """
        self.inner = inner

    def leq(self, other: "InverseLattice[L]") -> bool:
        """Inverted ordering: self ≤ other iff other.inner ≤ self.inner."""
        if not isinstance(other, InverseLattice):
            return False
        return other.inner.leq(self.inner)

    def join(self, other: "InverseLattice[L]") -> "InverseLattice[L]":
        """Inverted join: meet of inner elements."""
        if not isinstance(other, InverseLattice):
            raise TypeError("Can only join with another InverseLattice")
        return InverseLattice(self.inner.meet(other.inner))

    def meet(self, other: "InverseLattice[L]") -> "InverseLattice[L]":
        """Inverted meet: join of inner elements."""
        if not isinstance(other, InverseLattice):
            raise TypeError("Can only meet with another InverseLattice")
        return InverseLattice(self.inner.join(other.inner))

    def __repr__(self) -> str:
        return f"Inverse({repr(self.inner)})"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, InverseLattice) and self.inner == other.inner

    def __hash__(self) -> int:
        return hash(self.inner)


def join_labels(*labels: Lattice) -> Lattice:
    """
    Compute the join of multiple labels.
    
    Args:
        *labels: Variable number of labels to join
        
    Returns:
        The joined label
        
    Raises:
        ValueError: If no labels provided
        TypeError: If labels are not compatible for joining
    """
    if not labels:
        raise ValueError("At least one label must be provided")
    
    return reduce(lambda a, b: a.join(b), labels)


def meet_labels(*labels: Lattice) -> Lattice:
    """
    Compute the meet of multiple labels.
    
    Args:
        *labels: Variable number of labels to meet
        
    Returns:
        The meet label
        
    Raises:
        ValueError: If no labels provided
        TypeError: If labels are not compatible for meeting
    """
    if not labels:
        raise ValueError("At least one label must be provided")
    
    return reduce(lambda a, b: a.meet(b), labels)