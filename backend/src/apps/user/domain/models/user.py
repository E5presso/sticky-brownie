from uuid import UUID, uuid4
from typing import Self
from datetime import UTC, date, datetime

from spakky.core.mutability import immutable, mutable
from spakky.cryptography.password import Password
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent

from apps.user.domain.errors import (
    AuthenticationFailedError,
    InvalidPasswordResetTokenError,
)
from common.enums.gender import Gender
from common.enums.user_role import UserRole
from common.enums.user_status import UserStatus


@mutable
class User(AggregateRoot[UUID]):
    username: str
    """아이디"""
    password: str
    """비밀번호"""
    role: UserRole
    """사용자 역할"""
    status: UserStatus
    """사용자 상태"""
    name: str
    """사용자 이름"""
    address: str
    """사용자 주소"""
    phone_number: str
    """휴대폰 번호"""
    gender: Gender
    """성별"""
    birth_date: date
    """생년월일"""
    billing_name: str
    """예금주 이름"""
    password_reset_token: str | None
    """비밀번호 재설정 토큰"""
    terms_and_conditions_agreement: datetime
    """이용약관 동의 일시"""
    marketing_promotions_agreement: datetime | None
    """마케팅 수신 동의 일시"""
    remark: str
    """주석"""

    @property
    def is_password_forgotten(self) -> bool:
        return self.password_reset_token is not None

    @immutable
    class UserCreated(DomainEvent):
        uid: UUID

    @immutable
    class ForgotPassword(DomainEvent):
        uid: UUID

    @immutable
    class PasswordReset(DomainEvent):
        uid: UUID

    @immutable
    class PasswordUpdated(DomainEvent):
        uid: UUID

    @immutable
    class Authenticated(DomainEvent):
        uid: UUID
        ip_address: str
        user_agent: str

    @immutable
    class PhoneNumberUpdated(DomainEvent):
        uid: UUID

    @immutable
    class ProfileUpdated(DomainEvent):
        uid: UUID

    @immutable
    class MarketingPromotionsAgreed(DomainEvent):
        uid: UUID

    @immutable
    class MarketingPromotionsDisagreed(DomainEvent):
        uid: UUID

    @immutable
    class RemarkWritten(DomainEvent):
        uid: UUID

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        role: UserRole,
        name: str,
        address: str,
        phone_number: str,
        gender: Gender,
        birth_date: date,
        billing_name: str,
        terms_and_conditions_agreement: datetime,
        marketing_promotions_agreement: datetime | None = None,
    ) -> Self:
        self: Self = cls(
            uid=User.next_id(),
            username=username,
            password=Password(password=password).export,
            role=role,
            status=UserStatus.GREEN,
            name=name,
            address=address,
            phone_number=phone_number,
            gender=gender,
            birth_date=birth_date,
            billing_name=billing_name,
            password_reset_token=None,
            terms_and_conditions_agreement=terms_and_conditions_agreement,
            marketing_promotions_agreement=marketing_promotions_agreement,
            remark="",
        )
        self.add_event(self.UserCreated(uid=self.uid))
        return self

    def login(self, password: str, ip_address: str, user_agent: str) -> None:
        if not Password(password_hash=self.password).challenge(password):
            raise AuthenticationFailedError
        self.password_reset_token = None
        self.add_event(
            self.Authenticated(uid=self.uid, ip_address=ip_address, user_agent=user_agent)
        )

    def forgot_password(self, password_reset_token: str) -> None:
        self.password_reset_token = password_reset_token
        self.add_event(self.ForgotPassword(uid=self.uid))

    def reset_password(self, password_reset_token: str, new_password: str) -> None:
        if self.password_reset_token != password_reset_token:
            raise InvalidPasswordResetTokenError
        self.password = Password(password=new_password).export
        self.password_reset_token = None
        self.add_event(self.PasswordReset(uid=self.uid))

    def update_password(self, old_password: str, new_password: str) -> None:
        if not Password(password_hash=self.password).challenge(old_password):
            raise AuthenticationFailedError
        self.password = Password(password=new_password).export
        self.add_event(self.PasswordUpdated(uid=self.uid))

    def update_phone_number(self, phone_number: str) -> None:
        self.phone_number = phone_number
        self.add_event(self.PhoneNumberUpdated(uid=self.uid))

    def update_profile(
        self,
        name: str,
        address: str,
        gender: Gender,
        birth_date: date,
        billing_name: str,
    ) -> None:
        self.name = name
        self.address = address
        self.gender = gender
        self.birth_date = birth_date
        self.billing_name = billing_name
        self.add_event(self.ProfileUpdated(uid=self.uid))

    def agree_marketing_promotions(self) -> None:
        self.marketing_promotions_agreement = datetime.now(UTC)
        self.add_event(self.MarketingPromotionsAgreed(uid=self.uid))

    def disagree_marketing_promotions(self) -> None:
        self.marketing_promotions_agreement = None
        self.add_event(self.MarketingPromotionsDisagreed(uid=self.uid))

    def write_remark(self, remark: str) -> None:
        self.remark = remark
        self.add_event(self.RemarkWritten(uid=self.uid))
