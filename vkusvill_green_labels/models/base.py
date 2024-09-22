from advanced_alchemy.base import UUIDAuditBase


class Base(UUIDAuditBase):
    __abstract__ = True

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{self.__class__.__name__}({params})"
