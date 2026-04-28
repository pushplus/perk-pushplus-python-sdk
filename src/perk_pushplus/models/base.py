"""通用模型与 dataclass <-> dict 互转工具。"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

T = TypeVar("T")


def model_to_dict(obj: Any, *, drop_none: bool = True) -> Any:
    """递归把 dataclass / 枚举 / dict / list 转为可 JSON 序列化的 ``dict``。

    与 Java 端 ``JsonInclude.NON_NULL`` 行为对齐，默认丢弃 ``None`` 字段。
    """
    if obj is None:
        return None
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        result: Dict[str, Any] = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            converted = model_to_dict(value, drop_none=drop_none)
            if drop_none and converted is None:
                continue
            result[f.name] = converted
        return result
    if isinstance(obj, dict):
        return {
            k: model_to_dict(v, drop_none=drop_none)
            for k, v in obj.items()
            if not (drop_none and v is None)
        }
    if isinstance(obj, (list, tuple, set)):
        return [model_to_dict(v, drop_none=drop_none) for v in obj]
    return obj


def model_from_dict(cls: Type[T], data: Any) -> Optional[T]:
    """将 ``dict`` 反序列化为 dataclass 实例（递归处理嵌套 dataclass / 列表 / Optional / 枚举）。

    - 多余字段会被忽略（与 ``@JsonIgnoreProperties(ignoreUnknown=true)`` 等价）；
    - ``None`` 输入返回 ``None``；
    - 类型若为 :class:`Enum` 子类，则尝试用 ``cls(value)`` 构造，构造失败保留原值。
    """
    if data is None:
        return None
    origin = get_origin(cls)
    if origin is not None:
        if isinstance(origin, type) and is_dataclass(origin):
            return _from_dict_with_generics(origin, get_args(cls), data)  # type: ignore[return-value]
        return _convert_typed(cls, data)
    if isinstance(cls, type) and issubclass(cls, Enum):
        try:
            return cls(data)  # type: ignore[return-value]
        except ValueError:
            return data  # type: ignore[return-value]
    if not (isinstance(cls, type) and is_dataclass(cls)):
        return data  # type: ignore[return-value]
    if not isinstance(data, dict):
        return data  # type: ignore[return-value]

    try:
        type_hints = get_type_hints(cls)
    except Exception:  # noqa: BLE001
        type_hints = {f.name: f.type for f in fields(cls)}

    init_kwargs: Dict[str, Any] = {}
    field_names = {f.name for f in fields(cls)}
    for name in field_names:
        if name not in data:
            continue
        value = data[name]
        target_type = type_hints.get(name, Any)
        init_kwargs[name] = _convert_typed(target_type, value)
    return cls(**init_kwargs)  # type: ignore[arg-type]


def _resolve_typevars(target_type: Any, mapping: Dict[Any, Any]) -> Any:
    """递归把 ``TypeVar`` 替换成实际类型（用于支持 ``Generic`` dataclass）。"""

    if isinstance(target_type, TypeVar):  # type: ignore[misc]
        return mapping.get(target_type, Any)
    origin = get_origin(target_type)
    if origin is None:
        return target_type
    args = tuple(_resolve_typevars(a, mapping) for a in get_args(target_type))
    try:
        return target_type.copy_with(args)  # typing.GenericAlias 提供
    except AttributeError:
        try:
            return origin[args] if len(args) > 1 else origin[args[0]]
        except Exception:  # noqa: BLE001
            return target_type


def _from_dict_with_generics(cls: type, type_args: tuple, data: Any) -> Any:
    """使用泛型实参把 ``Generic`` dataclass 反序列化。"""

    if data is None:
        return None
    if not isinstance(data, dict):
        return data
    type_params = getattr(cls, "__parameters__", ())
    mapping: Dict[Any, Any] = {}
    for tp, ta in zip(type_params, type_args or ()):
        mapping[tp] = ta

    try:
        type_hints = get_type_hints(cls)
    except Exception:  # noqa: BLE001
        type_hints = {f.name: f.type for f in fields(cls)}

    init_kwargs: Dict[str, Any] = {}
    field_names = {f.name for f in fields(cls)}
    for name in field_names:
        if name not in data:
            continue
        value = data[name]
        target_type = type_hints.get(name, Any)
        target_type = _resolve_typevars(target_type, mapping)
        init_kwargs[name] = _convert_typed(target_type, value)
    return cls(**init_kwargs)


def _convert_typed(target_type: Any, value: Any) -> Any:
    if value is None:
        return None
    if target_type is Any or target_type is None:
        return value
    origin = get_origin(target_type)

    # Optional[X] / Union[...]
    if origin is Union:
        args = [a for a in get_args(target_type) if a is not type(None)]
        if len(args) == 1:
            return _convert_typed(args[0], value)
        for a in args:
            try:
                return _convert_typed(a, value)
            except Exception:  # noqa: BLE001
                continue
        return value

    if origin in (list, List):
        (item_type,) = get_args(target_type) or (Any,)
        if isinstance(value, list):
            return [_convert_typed(item_type, v) for v in value]
        return value

    if origin in (dict, Dict):
        args = get_args(target_type)
        v_type = args[1] if len(args) == 2 else Any
        if isinstance(value, dict):
            return {k: _convert_typed(v_type, v) for k, v in value.items()}
        return value

    if origin is not None and isinstance(origin, type) and is_dataclass(origin):
        type_args = get_args(target_type)
        return _from_dict_with_generics(origin, type_args, value)

    if isinstance(target_type, type):
        if issubclass(target_type, Enum):
            try:
                return target_type(value)
            except ValueError:
                return value
        if is_dataclass(target_type):
            return model_from_dict(target_type, value)
        if target_type is bool and not isinstance(value, bool):
            return bool(value)
        if target_type is int and not isinstance(value, bool):
            try:
                return int(value)
            except (TypeError, ValueError):
                return value
        if target_type is float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return value
        if target_type is str and not isinstance(value, str):
            return str(value)
    return value


@dataclass
class ApiResponse(Generic[T]):
    """PushPlus 接口统一响应。所有接口都遵循 ``{code, msg, data}`` 结构。"""

    code: Optional[int] = None
    msg: Optional[str] = None
    data: Optional[T] = None

    def is_success(self) -> bool:
        return self.code is not None and int(self.code) == 200


@dataclass
class PageQuery:
    """通用分页请求参数。"""

    current: Optional[int] = None
    """当前所在分页数，默认 1。"""
    pageSize: Optional[int] = None
    """每页大小，默认 20，最大 50。"""
    params: Optional[Dict[str, Any]] = None
    """部分接口需要的额外参数对象（如群组列表的 ``{topicType}``）。"""

    @classmethod
    def of(cls, current: Optional[int] = 1, page_size: Optional[int] = 20) -> "PageQuery":
        return cls(current=current, pageSize=page_size)


@dataclass
class PageResult(Generic[T]):
    """分页响应结构。"""

    pageNum: Optional[int] = None
    pageSize: Optional[int] = None
    total: Optional[int] = None
    pages: Optional[int] = None
    list: List[T] = field(default_factory=list)


__all__ = [
    "ApiResponse",
    "PageQuery",
    "PageResult",
    "model_to_dict",
    "model_from_dict",
]
