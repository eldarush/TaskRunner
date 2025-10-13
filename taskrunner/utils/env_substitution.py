import os
import re
from typing import Dict


def substitute_env_vars(config: Dict) -> Dict:
    def substitute_value(value):
        if isinstance(value, str):
            # Find all ${VAR_NAME} patterns and substitute them
            pattern = r'\$\{([^}]+)\}'

            def replacer(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))  # Return original if not found

            return re.sub(pattern, replacer, value)
        elif isinstance(value, dict):
            return {k: substitute_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [substitute_value(item) for item in value]
        else:
            return value

    return substitute_value(config)
