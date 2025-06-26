# meta developer: @xduko
# module: uxla

from .. import loader, utils
import random

class UxlaMod(loader.Module):
    """uxla gandon moduli"""
    strings = {"name": "Uxla"}

    async def client_ready(self, client, db):
        self.db = db

    async def uxlacmd(self, message):
        """Foydalanish: .uxla"""
        texts = [
            "Uxla yobanavrot soat 12 bold",
            "Qutoq bormi kechasi uxla gandonali",
            "Denaxoy zaybal uxla",
            "Tashaq bormi uka kechasi uxla",
            "Chuhoq uxla",
            "Uxla zaybal",
            "Asabim buzmasdan denaxoy uxla",
            "Uxla qoshnin amiga ski",
        ]
        await message.edit(random.choice(texts))
