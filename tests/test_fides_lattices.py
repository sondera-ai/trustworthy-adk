"""
Tests for Fides lattice system.

This module tests the mathematical lattice structures used for security labels
in the Fides Information Flow Control system.
"""

import pytest
from trustworthy.plugins.fides.lattices import (
    IntegrityLabel, PowersetLattice, ProductLabel, InverseLattice,
    join_labels, meet_labels
)


class TestIntegrityLabel:
    """Test the two-point integrity lattice."""
    
    def test_creation(self):
        """Test creating integrity labels."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        assert trusted.is_trusted is True
        assert untrusted.is_trusted is False
    
    def test_ordering(self):
        """Test the ordering relation: TRUSTED ≤ UNTRUSTED."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        # TRUSTED ≤ UNTRUSTED
        assert trusted.leq(untrusted)
        assert trusted <= untrusted
        
        # UNTRUSTED ≰ TRUSTED
        assert not untrusted.leq(trusted)
        assert not untrusted <= trusted
        
        # Reflexivity
        assert trusted.leq(trusted)
        assert untrusted.leq(untrusted)
    
    def test_join(self):
        """Test join operation: TRUSTED ∨ UNTRUSTED = UNTRUSTED."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        # TRUSTED ∨ UNTRUSTED = UNTRUSTED
        result = trusted.join(untrusted)
        assert result.is_trusted is False
        
        # UNTRUSTED ∨ TRUSTED = UNTRUSTED
        result = untrusted.join(trusted)
        assert result.is_trusted is False
        
        # Idempotency
        assert trusted.join(trusted).is_trusted is True
        assert untrusted.join(untrusted).is_trusted is False
    
    def test_meet(self):
        """Test meet operation: TRUSTED ∧ UNTRUSTED = TRUSTED."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        # TRUSTED ∧ UNTRUSTED = TRUSTED
        result = trusted.meet(untrusted)
        assert result.is_trusted is True
        
        # UNTRUSTED ∧ TRUSTED = TRUSTED
        result = untrusted.meet(trusted)
        assert result.is_trusted is True
        
        # Idempotency
        assert trusted.meet(trusted).is_trusted is True
        assert untrusted.meet(untrusted).is_trusted is False
    
    def test_operators(self):
        """Test operator overloads."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        # Join operator |
        assert (trusted | untrusted).is_trusted is False
        
        # Meet operator &
        assert (trusted & untrusted).is_trusted is True
    
    def test_equality(self):
        """Test equality and hashing."""
        trusted1 = IntegrityLabel.trusted()
        trusted2 = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        
        assert trusted1 == trusted2
        assert trusted1 != untrusted
        assert hash(trusted1) == hash(trusted2)


class TestPowersetLattice:
    """Test the powerset lattice for confidentiality."""
    
    def test_creation(self):
        """Test creating powerset lattice elements."""
        universe = frozenset(["alice", "bob", "charlie"])
        subset = frozenset(["alice", "bob"])
        
        lattice_elem = PowersetLattice(subset, universe)
        assert lattice_elem.subset == subset
        assert lattice_elem.universe == universe
    
    def test_invalid_creation(self):
        """Test that invalid subsets raise errors."""
        universe = frozenset(["alice", "bob"])
        invalid_subset = frozenset(["alice", "charlie"])  # charlie not in universe
        
        with pytest.raises(ValueError):
            PowersetLattice(invalid_subset, universe)
    
    def test_ordering(self):
        """Test subset inclusion ordering."""
        universe = frozenset(["alice", "bob", "charlie"])
        small = PowersetLattice(frozenset(["alice"]), universe)
        large = PowersetLattice(frozenset(["alice", "bob"]), universe)
        
        # Smaller subset ≤ larger subset
        assert small.leq(large)
        assert not large.leq(small)
        
        # Reflexivity
        assert small.leq(small)
        assert large.leq(large)
    
    def test_join(self):
        """Test join operation (union)."""
        universe = frozenset(["alice", "bob", "charlie"])
        set1 = PowersetLattice(frozenset(["alice"]), universe)
        set2 = PowersetLattice(frozenset(["bob"]), universe)
        
        result = set1.join(set2)
        assert result.subset == frozenset(["alice", "bob"])
    
    def test_meet(self):
        """Test meet operation (intersection)."""
        universe = frozenset(["alice", "bob", "charlie"])
        set1 = PowersetLattice(frozenset(["alice", "bob"]), universe)
        set2 = PowersetLattice(frozenset(["bob", "charlie"]), universe)
        
        result = set1.meet(set2)
        assert result.subset == frozenset(["bob"])
    
    def test_bottom_top(self):
        """Test bottom and top elements."""
        universe = frozenset(["alice", "bob", "charlie"])
        
        bottom = PowersetLattice.bottom(universe)
        assert bottom.subset == frozenset()
        
        top = PowersetLattice.top(universe)
        assert top.subset == universe
        
        # Bottom ≤ everything
        middle = PowersetLattice(frozenset(["alice"]), universe)
        assert bottom.leq(middle)
        assert middle.leq(top)


class TestProductLabel:
    """Test the product lattice combining two dimensions."""
    
    def test_creation(self):
        """Test creating product labels."""
        integrity = IntegrityLabel.trusted()
        universe = frozenset(["alice", "bob"])
        confidentiality = PowersetLattice(frozenset(["alice"]), universe)
        
        product = ProductLabel(integrity, confidentiality)
        assert product.left == integrity
        assert product.right == confidentiality
    
    def test_ordering(self):
        """Test component-wise ordering."""
        # Create components
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        universe = frozenset(["alice", "bob"])
        small_conf = PowersetLattice(frozenset(["alice"]), universe)
        large_conf = PowersetLattice(frozenset(["alice", "bob"]), universe)
        
        # Create product labels
        label1 = ProductLabel(trusted, small_conf)
        label2 = ProductLabel(untrusted, large_conf)
        label3 = ProductLabel(trusted, large_conf)
        
        # (trusted, small) ≤ (untrusted, large)
        assert label1.leq(label2)
        
        # (trusted, small) ≤ (trusted, large)
        assert label1.leq(label3)
        
        # (untrusted, large) ≰ (trusted, small)
        assert not label2.leq(label1)
    
    def test_join(self):
        """Test component-wise join."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        universe = frozenset(["alice", "bob"])
        conf1 = PowersetLattice(frozenset(["alice"]), universe)
        conf2 = PowersetLattice(frozenset(["bob"]), universe)
        
        label1 = ProductLabel(trusted, conf1)
        label2 = ProductLabel(untrusted, conf2)
        
        result = label1.join(label2)
        
        # Should be (untrusted, {alice, bob})
        assert result.left.is_trusted is False
        assert result.right.subset == frozenset(["alice", "bob"])
    
    def test_meet(self):
        """Test component-wise meet."""
        trusted = IntegrityLabel.trusted()
        untrusted = IntegrityLabel.untrusted()
        universe = frozenset(["alice", "bob"])
        conf1 = PowersetLattice(frozenset(["alice", "bob"]), universe)
        conf2 = PowersetLattice(frozenset(["bob"]), universe)
        
        label1 = ProductLabel(trusted, conf1)
        label2 = ProductLabel(untrusted, conf2)
        
        result = label1.meet(label2)
        
        # Should be (trusted, {bob})
        assert result.left.is_trusted is True
        assert result.right.subset == frozenset(["bob"])


class TestInverseLattice:
    """Test the inverse lattice."""
    
    def test_ordering_inversion(self):
        """Test that ordering is inverted."""
        universe = frozenset(["alice", "bob"])
        small = PowersetLattice(frozenset(["alice"]), universe)
        large = PowersetLattice(frozenset(["alice", "bob"]), universe)
        
        inv_small = InverseLattice(small)
        inv_large = InverseLattice(large)
        
        # In original: small ≤ large
        assert small.leq(large)
        
        # In inverse: inv_large ≤ inv_small
        assert inv_large.leq(inv_small)
        assert not inv_small.leq(inv_large)
    
    def test_operations_swapped(self):
        """Test that join and meet are swapped."""
        universe = frozenset(["alice", "bob"])
        set1 = PowersetLattice(frozenset(["alice"]), universe)
        set2 = PowersetLattice(frozenset(["bob"]), universe)
        
        inv1 = InverseLattice(set1)
        inv2 = InverseLattice(set2)
        
        # Join in inverse = meet in original
        inv_join = inv1.join(inv2)
        orig_meet = set1.meet(set2)
        assert inv_join.inner.subset == orig_meet.subset
        
        # Meet in inverse = join in original
        inv_meet = inv1.meet(inv2)
        orig_join = set1.join(set2)
        assert inv_meet.inner.subset == orig_join.subset


class TestLabelOperations:
    """Test utility functions for label operations."""
    
    def test_join_labels(self):
        """Test joining multiple labels."""
        label1 = IntegrityLabel.trusted()
        label2 = IntegrityLabel.untrusted()
        label3 = IntegrityLabel.trusted()
        
        result = join_labels(label1, label2, label3)
        assert result.is_trusted is False  # Should be untrusted
    
    def test_meet_labels(self):
        """Test meeting multiple labels."""
        label1 = IntegrityLabel.trusted()
        label2 = IntegrityLabel.untrusted()
        label3 = IntegrityLabel.trusted()
        
        result = meet_labels(label1, label2, label3)
        assert result.is_trusted is True  # Should be trusted
    
    def test_empty_operations(self):
        """Test operations with no labels."""
        with pytest.raises(ValueError):
            join_labels()
        
        with pytest.raises(ValueError):
            meet_labels()