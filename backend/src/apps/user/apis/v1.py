from datetime import date

from pydantic import BaseModel
from spakky.bean.autowired import autowired
from spakky.extensions.logging import AsyncLogging
from spakky.stereotype.controller import Controller
from spakky_fastapi.routing import post

from src.apps.user.domain.models.gender import Gender
from src.apps.user.domain.ports.usecases.register import (
    IAsyncRegisterCommandUseCase,
    RegisterCommand,
)


class RegisterRequest(BaseModel):
    account_name: str
    password: str
    name: str
    address: str
    phone_number: str
    gender: Gender
    birth_date: date
    billing_name: str
    terms_and_conditions_agreement: bool
    marketing_promotions_agreement: bool


@Controller("/users/v1")
class UserRestApiController:
    register: IAsyncRegisterCommandUseCase

    @autowired
    def __init__(self, register: IAsyncRegisterCommandUseCase) -> None:
        self.register = register

    @post("/register")
    @AsyncLogging()
    async def register_user(self, request: RegisterRequest) -> None:
        await self.register.execute(
            command=RegisterCommand(
                username=request.account_name,
                password=request.password,
                name=request.name,
                address=request.address,
                phone_number=request.phone_number,
                gender=request.gender,
                birth_date=request.birth_date,
                billing_name=request.billing_name,
                terms_and_conditions_agreement=request.terms_and_conditions_agreement,
                marketing_promotions_agreement=request.marketing_promotions_agreement,
            )
        )
