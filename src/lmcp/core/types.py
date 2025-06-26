from typing import Union, List, Dict, TypeAlias
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# Describe the type of data returned by model_dump()
SerializableData: TypeAlias = Union[Dict[str, "SerializableData"], List["SerializableData"], str, int, float, bool, None]

# Describe the rich text structure output by ruamel.yaml
CommentedStructure: TypeAlias = Union[CommentedMap, CommentedSeq, str, int, float, bool, None]