import json

from pydantic import BaseModel, ValidationError


def coerce_to_model[T: BaseModel](model: type[T], raw: str) -> T:
    try:
        return model.model_validate_json(raw)

    except ValidationError:
        pass

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        obj = json.loads(raw[start:end])
        return model.model_validate(obj)

    except Exception as e:
        raise RuntimeError(f"Could not coerce output to {model.__name__}: {e}") from e
