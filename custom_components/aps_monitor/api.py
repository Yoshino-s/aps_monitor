import json
import logging
from typing import Optional

import aiohttp

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ApsApiClient:
    def __init__(
        self, username: str, password: str, session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        if session:
            self._session = session
        else:
            self._session = aiohttp.ClientSession(
                trust_env=True,
                base_url="https://aps.ytl-s.com",
            )

    async def async_login(self):
        """
        ScriptManager1=UpdatePanel2%7CButton1&__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwULLTE3MTE5NDQzMjVkZCuJu%2FP8CZeFishMjJCy%2FagTThlEjtHt7cDdPLxELxo1&__VIEWSTATEGENERATOR=997ED80C&Label3=8&username=15961477380&password=123456&__ASYNCPOST=true&Button1=%E7%99%BB%E5%BD%95
        """
        return '电表查询' in await (await self._session.post("/aps/aps.aspx", data={
            "username": self._username,
            "password": self._password,
            "Button1": "登录",
            "__ASYNCPOST": "false",
            "__VIEWSTATE": "/wEPDwULLTE3MTE5NDQzMjVkZCuJu/P8CZeFishMjJCy/agTThlEjtHt7cDdPLxELxo1",
        })).text()

    async def async_get_meter_list(self):
        try:
            return json.loads(await (await self._session.post("/aps/Owner/Manage.ashx", params={
                "Method": "GetFMeters"
            }, json={
                "PageSize":999999,"SortAsc":0,"MeterGuanXi":{"guanxi":"Contain","value":""},"NameGuanXi":{"guanxi":"Contain","value":""},"KwhGuanXi":{"guanxi":"NotMoreThan","value":""},"TimeGuanXi":{"guanxi":"NotMoreThan","value":""}
            })).text())['value']['Items']
        except:
            r = await self.async_login()
            if r:
                return await self.async_get_meter_list()
            else:
                _LOGGER.error("login failed", exc_info=True)
                raise

    async def async_get_instant(self, id: str):
        try:
            return json.loads(await (await self._session.post("/aps/Operate.aspx/GetInstant", json={
                'metid':id
            })).text())['d']['value']
        except:
            r = await self.async_login()
            if r:
                return await self.async_get_instant(id)
            else:
                _LOGGER.error("login failed", exc_info=True)
                raise

if __name__ == "__main__":
    import asyncio
    async def main():
        async with aiohttp.ClientSession():
            api = ApsApiClient("15961477380", "123456")
            resp = await api.async_login()
            if resp:
                list =await api.async_get_meter_list()
                print(list)
                for meter in list:
                    print(await api.async_get_instant(str(int(meter["Meter"]["MeterID"]))))
            else:
                raise Exception("登录失败")
    asyncio.run(main())
