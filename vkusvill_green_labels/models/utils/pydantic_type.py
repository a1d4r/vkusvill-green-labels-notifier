from typing import Any, TypeVar

import sqlalchemy as sa

from pydantic import BaseModel, TypeAdapter
from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.type_api import TypeEngine

ModelT = TypeVar("ModelT", bound=BaseModel)


class PydanticType(sa.types.TypeDecorator[ModelT]):
    """Pydantic type.
    Inspired by: https://gist.github.com/imankulov/4051b7805ad737ace7d8de3d3f934d6b

    SAVING:
    - Uses SQLAlchemy JSON type under the hood.
    - Acceps the pydantic model and converts it to a dict on save.
    - SQLAlchemy engine JSON-encodes the dict to a string.
    RETRIEVING:
    - Pulls the string from the database.
    - SQLAlchemy engine JSON-decodes the string to a dict.
    - Uses the dict to create a pydantic model.
    """

    cache_ok = True
    impl = JSONB

    def __init__(self, pydantic_type: type[ModelT]) -> None:
        super().__init__()
        self.pydantic_type = pydantic_type
        self.adapter = TypeAdapter(pydantic_type)

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())  # type: ignore[no-untyped-call]
        return dialect.type_descriptor(sa.JSON())

    def process_bind_param(self, value: ModelT | None, _dialect: Dialect) -> Any:
        if value is None:
            return None
        return value.model_dump(mode="json")

    def process_result_value(self, value: Any, _dialect: Dialect) -> ModelT | None:
        if value is None:
            return None
        return self.adapter.validate_python(value)

    def __repr__(self) -> str:
        # Used by alembic
        return f"PydanticType({self.pydantic_type.__name__})"
