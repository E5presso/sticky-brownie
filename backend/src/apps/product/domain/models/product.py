from uuid import UUID, uuid4
from typing import Self, Sequence
from datetime import date, datetime

from spakky.core.mutability import immutable, mutable
from spakky.cryptography.password import Password
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@mutable
class Product(AggregateRoot[UUID]):
    thumbnail: str
    """썸네일"""
    title: str
    """제목"""
    subtitle: str
    """부제목"""
    category_ids: Sequence[UUID]
    """카테고리 ID 목록"""
    price: int
    """가격"""
    detail_page_html: str
    """상세 페이지 HTML"""
    is_visible: bool
    """상품 노출 여부"""
