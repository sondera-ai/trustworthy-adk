"""
Label Propagation System for Pydantic Schemas

This module implements the label propagation system that allows security labels
to be attached to data and automatically propagated through tool calls and
agent operations. Based on the MetaValue approach from the Fides tutorial.

Key Components:
- MetaValue: Generic wrapper for attaching security labels to data
- LabeledData: Type alias for commonly used labeled data patterns
- Automatic label propagation through Pydantic schema validation
- Integration with ADK tool calling mechanisms
"""

from typing import Any, Dict, Generic, TypeVar, get_args, Optional, Union
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from functools import reduce

from .lattices import Lattice, join_labels


T = TypeVar("T")


class MetaValue(Generic[T]):
    """
    Generic wrapper for attaching security labels to data values.
    
    This class allows any data value to be augmented with security metadata,
    particularly security labels from lattices. The wrapper is transparent
    for most operations, delegating attribute access to the inner value.
    
    Example:
        # Create labeled data
        email_content = MetaValue(
            "Hello, this is a test email",
            metadata={"integrity": IntegrityLabel.trusted()}
        )
        
        # Access the value transparently
        print(len(email_content))  # Works like a string
        
        # Access the security label
        integrity = email_content.metadata["integrity"]
    """

    def __init__(self, value: T, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a labeled value.
        
        Args:
            value: The actual data value
            metadata: Dictionary containing security labels and other metadata
        """
        self.value = value
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return repr(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, MetaValue):
            return self.value < other.value  # type: ignore
        else:
            return self.value < other  # type: ignore

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, MetaValue):
            return self.value > other.value  # type: ignore
        else:
            return self.value > other  # type: ignore

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MetaValue):
            return self.value == other.value
        else:
            return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)  # type: ignore

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]  # type: ignore

    def __setitem__(self, key: Any, value: Any) -> None:
        self.value[key] = value  # type: ignore

    def __iter__(self):
        return iter(self.value)  # type: ignore

    def __getattr__(self, name: str) -> Any:
        """Delegate all other attribute access to the inner value."""
        return getattr(self.value, name)

    def get_label(self, label_type: str) -> Optional[Lattice]:
        """
        Get a specific security label from the metadata.
        
        Args:
            label_type: The type of label to retrieve (e.g., "integrity", "confidentiality")
            
        Returns:
            The security label if present, None otherwise
        """
        return self.metadata.get(label_type)

    def set_label(self, label_type: str, label: Lattice) -> "MetaValue[T]":
        """
        Create a new MetaValue with an updated security label.
        
        Args:
            label_type: The type of label to set
            label: The security label to set
            
        Returns:
            A new MetaValue with the updated label
        """
        new_metadata = self.metadata.copy()
        new_metadata[label_type] = label
        return MetaValue(self.value, new_metadata)

    def join_labels(self, other: "MetaValue[Any]", label_types: Optional[list[str]] = None) -> Dict[str, Lattice]:
        """
        Compute the join of security labels with another MetaValue.
        
        Args:
            other: The other MetaValue to join labels with
            label_types: Specific label types to join, or None for all common types
            
        Returns:
            Dictionary of joined labels
        """
        if label_types is None:
            label_types = list(set(self.metadata.keys()) & set(other.metadata.keys()))
        
        joined_labels = {}
        for label_type in label_types:
            self_label = self.get_label(label_type)
            other_label = other.get_label(label_type)
            
            if self_label is not None and other_label is not None:
                joined_labels[label_type] = self_label.join(other_label)
            elif self_label is not None:
                joined_labels[label_type] = self_label
            elif other_label is not None:
                joined_labels[label_type] = other_label
        
        return joined_labels

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        """
        Pydantic core schema for MetaValue to enable automatic validation and serialization.
        
        This allows MetaValue to be used seamlessly in Pydantic models while preserving
        the security labels during validation and serialization.
        """
        # Find the inner type T from MetaValue[T]
        args = get_args(source)
        if args:
            inner_type = args[0]
            # Validator for T
            inner_schema = handler.generate_schema(inner_type)
        else:
            # Fallback to any type if no generic parameter
            inner_schema = core_schema.any_schema()

        # Schema for MetaValue instances
        instance_schema = core_schema.is_instance_schema(cls)

        # Wrap T into MetaValue
        wrap_schema = core_schema.no_info_after_validator_function(
            lambda x: cls(x) if not isinstance(x, cls) else x,
            inner_schema
        )

        # Union schema that accepts either MetaValue[T] or T
        union = core_schema.union_schema([instance_schema, wrap_schema])

        return core_schema.json_or_python_schema(
            json_schema=union,
            python_schema=union,
        )


# Type aliases for commonly used labeled data patterns
LabeledData = MetaValue[Any]
LabeledString = MetaValue[str]
LabeledInt = MetaValue[int]
LabeledBool = MetaValue[bool]
LabeledList = MetaValue[list]
LabeledDict = MetaValue[dict]


def propagate_labels(*values: MetaValue[Any], label_types: Optional[list[str]] = None) -> Dict[str, Lattice]:
    """
    Propagate security labels from multiple MetaValues using join operations.
    
    This function computes the join (least upper bound) of security labels
    across multiple labeled values, implementing the standard label propagation
    semantics for information flow control.
    
    Args:
        *values: Variable number of MetaValues to propagate labels from
        label_types: Specific label types to propagate, or None for all common types
        
    Returns:
        Dictionary of propagated labels
        
    Example:
        email1 = MetaValue("Hello", {"integrity": IntegrityLabel.trusted()})
        email2 = MetaValue("World", {"integrity": IntegrityLabel.untrusted()})
        
        # Propagate labels - result will be untrusted (join of trusted and untrusted)
        labels = propagate_labels(email1, email2, label_types=["integrity"])
    """
    if not values:
        return {}
    
    # Determine which label types to propagate
    if label_types is None:
        all_label_types = set()
        for value in values:
            all_label_types.update(value.metadata.keys())
        label_types = list(all_label_types)
    
    propagated_labels = {}
    
    for label_type in label_types:
        # Collect all labels of this type
        labels_of_type = []
        for value in values:
            label = value.get_label(label_type)
            if label is not None:
                labels_of_type.append(label)
        
        # Compute the join if we have any labels
        if labels_of_type:
            propagated_labels[label_type] = join_labels(*labels_of_type)
    
    return propagated_labels


def create_labeled_result(value: T, input_labels: Dict[str, Lattice]) -> MetaValue[T]:
    """
    Create a labeled result value with propagated security labels.
    
    This is a convenience function for creating tool results with appropriate
    security labels based on the inputs that were used to compute the result.
    
    Args:
        value: The result value
        input_labels: Security labels propagated from inputs
        
    Returns:
        A MetaValue containing the result with security labels
    """
    return MetaValue(value, metadata=input_labels)


class LabelPropagationMixin:
    """
    Mixin class for Pydantic models that need automatic label propagation.
    
    This mixin provides utilities for models that contain MetaValue fields
    and need to automatically propagate security labels during validation
    and processing.
    """

    def extract_labels(self, label_types: Optional[list[str]] = None) -> Dict[str, Lattice]:
        """
        Extract and propagate security labels from all MetaValue fields in this model.
        
        Args:
            label_types: Specific label types to extract, or None for all types
            
        Returns:
            Dictionary of propagated labels
        """
        meta_values = []
        
        # Find all MetaValue fields
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, MetaValue):
                meta_values.append(field_value)
            elif isinstance(field_value, list):
                # Handle lists of MetaValues
                for item in field_value:
                    if isinstance(item, MetaValue):
                        meta_values.append(item)
            elif isinstance(field_value, dict):
                # Handle dictionaries with MetaValue values
                for item in field_value.values():
                    if isinstance(item, MetaValue):
                        meta_values.append(item)
        
        return propagate_labels(*meta_values, label_types=label_types)

    def create_labeled_field(self, field_name: str, value: Any, 
                           propagated_labels: Optional[Dict[str, Lattice]] = None) -> MetaValue[Any]:
        """
        Create a labeled field value with appropriate security labels.
        
        Args:
            field_name: Name of the field
            value: The field value
            propagated_labels: Labels to attach, or None to extract from model
            
        Returns:
            A MetaValue with appropriate security labels
        """
        if propagated_labels is None:
            propagated_labels = self.extract_labels()
        
        return MetaValue(value, metadata=propagated_labels)


# Utility functions for common label operations

def label_as_trusted(value: T, additional_labels: Optional[Dict[str, Lattice]] = None) -> MetaValue[T]:
    """Create a MetaValue labeled as trusted."""
    from .lattices import IntegrityLabel
    
    metadata = {"integrity": IntegrityLabel.trusted()}
    if additional_labels:
        metadata.update(additional_labels)
    
    return MetaValue(value, metadata)


def label_as_untrusted(value: T, additional_labels: Optional[Dict[str, Lattice]] = None) -> MetaValue[T]:
    """Create a MetaValue labeled as untrusted."""
    from .lattices import IntegrityLabel
    
    metadata = {"integrity": IntegrityLabel.untrusted()}
    if additional_labels:
        metadata.update(additional_labels)
    
    return MetaValue(value, metadata)


def label_with_readers(value: T, readers: frozenset[str], universe: frozenset[str], 
                      additional_labels: Optional[Dict[str, Lattice]] = None) -> MetaValue[T]:
    """Create a MetaValue with confidentiality labels based on readers."""
    from .lattices import PowersetLattice, InverseLattice
    
    confidentiality = InverseLattice(PowersetLattice(readers, universe))
    metadata = {"confidentiality": confidentiality}
    if additional_labels:
        metadata.update(additional_labels)
    
    return MetaValue(value, metadata)