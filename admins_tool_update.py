#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors
#    update module dev: @xduko 2025:06:24

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
from .. import loader, utils, security
import logging
from datetime import timedelta, datetime
import re

from telethon.tl.types import ChatAdminRights, ChatBannedRights, PeerUser, PeerChannel
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.functions.messages import EditChatAdminRequest

logger = logging.getLogger(__name__)


@loader.tds
class BanMod(loader.Module):
    """Админтулс — ban, unban, kick, promote, demote, mute, unmute, pin, unpin"""
    strings = {
        "name": "AdminTools",
        "not_supergroup": "<b>Это не супергруппа!</b>",
        "not_group": "<b>Это не группа!</b>",
        "ban_none": "<b>Кого банить?</b>",
        "unban_none": "<b>Кого разбанить?</b>",
        "kick_none": "<b>Кто хочет принудительно покинуть чат?</b>",
        "promote_none": "<b>Кто хочет опку?</b>",
        "demote_none": "<b>Укажи с кого снять админку?</b>",
        "mute_none": "<b>Кого замьютить?</b>",
        "unmute_none": "<b>Кого размьютить?</b>",
        "who": "<b>Кого...?</b>",
        "not_admin": "<b>Я не администратор...</b>",
        "banned": "<code>{}</code> <b>получил бан!</b> ID: <code>{}</code>",
        "unbanned": "<code>{}</code> <b>разбанен!</b> ID: <code>{}</code>",
        "kicked": "<code>{}</code> <b>кикнут!</b> ID: <code>{}</code>",
        "promoted": "<code>{}</code> <b>стал админом!</b> ID: <code>{}</code>",
        "demoted": "<code>{}</code> <b>лишён админки!</b> ID: <code>{}</code>",
        "muted": "<code>{}</code> <b>замьючен на {}</b> ID: <code>{}</code>",
        "unmuted": "<code>{}</code> <b>размьючен</b> ID: <code>{}</code>",
        "pin_none": "<b>Ответь на сообщение, чтобы закрепить!</b>",
        "unpin_done": "<b>Сообщение откреплено.</b>"
    }

    async def client_ready(self, client, db):
        self.client = client

    def _parse_time(self, text):
        match = re.fullmatch(r"(\d+)([smhdwM])", text)
        if not match:
            return None
        num, unit = int(match[1]), match[2]
        return timedelta(seconds=num) if unit == "s" else \
               timedelta(minutes=num) if unit == "m" else \
               timedelta(hours=num) if unit == "h" else \
               timedelta(days=num) if unit == "d" else \
               timedelta(weeks=num) if unit == "w" else \
               timedelta(days=30*num) if unit == "M" else None

    async def _get_user(self, message, none_text):
        if message.is_reply:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, none_text)
                return None
            return await utils.get_user(reply)
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, none_text)
            return None
        who = int(args[0]) if args[0].isdigit() else args[0]
        try:
            return await self.client.get_entity(who)
        except Exception:
            await utils.answer(message, self.strings("who", message))
            return None

    @loader.group_admin_ban_users
    async def bancmd(self, message):
        """Бан"""
        user = await self._get_user(message, self.strings("ban_none", message))
        if not user:
            return
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                ChatBannedRights(until_date=None, view_messages=True)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("banned", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    async def unbancmd(self, message):
        """Разбан"""
        user = await self._get_user(message, self.strings("unban_none", message))
        if not user:
            return
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                ChatBannedRights(until_date=None, view_messages=False)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("unbanned", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    async def kickcmd(self, message):
        """Кик"""
        user = await self._get_user(message, self.strings("kick_none", message))
        if not user:
            return
        try:
            await self.client.kick_participant(message.chat_id, user.id)
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("kicked", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    async def promotecmd(self, message):
        """Админка"""
        args = utils.get_args(message)
        user = await self._get_user(message, self.strings("promote_none", message))
        if not user:
            return
        rank = ' '.join(args[1:]) if len(args) > 1 else ""
        rights = ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=True,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, add_admins=False, anonymous=False, manage_call=True)
        try:
            await self.client(EditAdminRequest(message.chat_id, user.id, rights, rank))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("promoted", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    async def demotecmd(self, message):
        """Снять админку"""
        user = await self._get_user(message, self.strings("demote_none", message))
        if not user:
            return
        try:
            await self.client(EditAdminRequest(message.chat_id, user.id,
                ChatAdminRights(False, False, False, False, False, False, False, False, False), ""))
        except BadRequestError:
            try:
                await self.client(EditChatAdminRequest(message.chat_id, user.id, False))
            except:
                return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("demoted", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    async def mutecmd(self, message):
        """Мут (например: .mute @user 10m)"""
        args = utils.get_args(message)
        user = await self._get_user(message, self.strings("mute_none", message))
        if not user:
            return
        delta = self._parse_time(args[1]) if len(args) > 1 else timedelta(days=365)
        until = datetime.utcnow() + delta
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                ChatBannedRights(until_date=until, send_messages=True)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        duration = args[1] if len(args) > 1 else "навсегда"
        await utils.answer(message, self.strings("muted", message).format(utils.escape_html(user.first_name), duration, user.id))

    @loader.group_admin_ban_users
    async def unmutecmd(self, message):
        """Размьютить"""
        user = await self._get_user(message, self.strings("unmute_none", message))
        if not user:
            return
        try:
            await self.client(EditBannedRequest(message.chat_id, user.id,
                ChatBannedRights(until_date=None, send_messages=False)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))
        await utils.answer(message, self.strings("unmuted", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_pin_messages
    async def pincmd(self, message):
        """Закрепить сообщение (реплай)"""
        if not message.is_reply:
            return await utils.answer(message, self.strings("pin_none", message))
        await self.client.pin_message(message.chat_id, message.reply_to_msg_id, notify=False)

    @loader.group_admin_pin_messages
    async def unpincmd(self, message):
        """Открепить сообщение"""
        await self.client.unpin_message(message.chat_id)
        await utils.answer(message, self.strings("unpin_done", message))
