"""Account: who you are and how many credits you have left."""

from __future__ import annotations

from secretvoice.types import Subscription, User


class Account:
    def __init__(self, client):
        self._client = client

    def user(self) -> User:
        return User.from_dict(self._client.request("GET", "/v1/user").json())

    def subscription(self) -> Subscription:
        return Subscription.from_dict(
            self._client.request("GET", "/v1/user/subscription").json()
        )

    def credits(self) -> int:
        """Remaining character credits for this billing cycle."""
        sub = self.subscription()
        return sub.character_count or 0


class AsyncAccount:
    def __init__(self, client):
        self._client = client

    async def user(self) -> User:
        return User.from_dict((await self._client.request("GET", "/v1/user")).json())

    async def subscription(self) -> Subscription:
        return Subscription.from_dict(
            (await self._client.request("GET", "/v1/user/subscription")).json()
        )

    async def credits(self) -> int:
        sub = await self.subscription()
        return sub.character_count or 0