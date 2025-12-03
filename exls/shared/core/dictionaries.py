from typing import Any, Dict, cast


def deep_merge(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Deep merges multiple dictionaries.
    Later dictionaries override earlier ones.
    Nested dictionaries are merged recursively.

    Args:
        *dicts: Variable number of dictionaries to merge.

    Returns:
        A new dictionary containing the merged result.
    """
    result: Dict[Any, Any] = {}
    for d in dicts:
        for k, v in d.items():
            if k in result and isinstance(result[k], Dict) and isinstance(v, Dict):
                result[k] = deep_merge(
                    cast(Dict[Any, Any], result[k]), cast(Dict[Any, Any], v)
                )
            else:
                result[k] = v
    return result
