"""
Fides: Information Flow Control for AI Agents

This package implements the Fides system for securing AI agents with Information-Flow Control (IFC).
Based on the paper "Securing AI Agents with Information-Flow Control" by Costa et al.

Key Components:
- Lattice-based security labels for confidentiality and integrity
- Dynamic taint tracking through agent planning loops
- Policy enforcement engine for deterministic security guarantees
- Integration with Google ADK plugin architecture

Usage:
    from trustworthy.plugins.fides import FidesPlugin, FidesConfig
    
    config = FidesConfig(
        enable_integrity_protection=True,
        enable_confidentiality_protection=True,
        halt_on_policy_violation=True
    )
    
    plugin = FidesPlugin(config)
"""

from .plugin import FidesPlugin, FidesConfig
from .labels import label_as_trusted, label_as_untrusted, label_with_readers, MetaValue, LabeledData
from .lattices import (
    Lattice,
    IntegrityLabel,
    PowersetLattice,
    ProductLabel,
    InverseLattice,
)
from .policies import Policy, NoExfiltrationPolicy, IntegrityProtectionPolicy
from .planner import IFCPlanner

__all__ = [
    "FidesPlugin",
    "FidesConfig", 
    "label_as_trusted",
    "label_as_untrusted", 
    "label_with_readers",
    "Lattice",
    "IntegrityLabel",
    "PowersetLattice",
    "ProductLabel",
    "InverseLattice",
    "MetaValue",
    "LabeledData",
    "Policy",
    "NoExfiltrationPolicy",
    "IntegrityProtectionPolicy",
    "IFCPlanner",
]

__version__ = "0.1.0"