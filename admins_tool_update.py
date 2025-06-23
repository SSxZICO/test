#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors
#    update module dev: @xduko

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

from .. import loader, utils, security
import logging

from telethon.tl.types import ChatAdminRights, ChatBannedRights, PeerUser, PeerChannel
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest
from telethon.tl.functions.messages import EditChatAdminRequest

logger = logging.getLogger(__name__)

@loader.tds
class BanMod(loader.Module):
    """Админтулс"""
    strings = {
        "name": "AdminTools",
        "not_supergroup": "<b>Это не супергруппа!</b>",
        "not_group": "<b>Это не группа!</b>",
        "ban_none": "<b>Кого банить?</b>",
        "unban_none": "<b>Кого разбанить?</b>",
        "kick_none": "<b>Кто хочет принудительно покинуть чат?</b>",
        "promote_none": "<b>Кто хочет опку?</b>",
        "demote_none": "<b>Укажи с кого снять админку?</b>",
        "who": "<b>Кого...?</b>",
        "not_admin": "<b>Я не администратор...</b>",
        "banned": "<code>{}</code> <b>Получил бан!</b>\n<b>ID:</b> <code>{}</code>",
        "unbanned": "<code>{}</code> <b>Получил разбан!</b>\n<b>ID:</b> <code>{}</code>",
        "kicked": "<code>{}</code> <b>Был кикнут!</b>\n<b>ID:</b> <code>{}</code>",
        "promoted": "<code>{}</code> <b>Получил права администратора!</b>\n<b>ID:</b> <code>{}</code>",
        "demoted": "<code>{}</code> <b>Потерял права администратора!</b>\n<b>ID:</b> <code>{}</code>"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.group_admin_ban_users
    @loader.ratelimit
    async def bancmd(self, message):
        """Бан в чате"""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings("not_supergroup", message))

        user = await self._get_user(message, self.strings("ban_none", message))
        if not user:
            return

        try:
            await self.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(view_messages=True)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))

        await self.allmodules.log("ban", group=message.chat_id, affected_uids=[user.id])
        await utils.answer(message, self.strings("banned", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    @loader.ratelimit
    async def unbancmd(self, message):
        """Разбан в чате"""
        if not isinstance(message.to_id, PeerChannel):
            return await utils.answer(message, self.strings("not_supergroup", message))

        user = await self._get_user(message, self.strings("unban_none", message))
        if not user:
            return

        try:
            await self.client(EditBannedRequest(message.chat_id, user.id, ChatBannedRights(view_messages=False)))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))

        await self.allmodules.log("unban", group=message.chat_id, affected_uids=[user.id])
        await utils.answer(message, self.strings("unbanned", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_ban_users
    @loader.ratelimit
    async def kickcmd(self, message):
        """Кикнуть из чата"""
        if isinstance(message.to_id, PeerUser):
            return await utils.answer(message, self.strings("not_group", message))

        user = await self._get_user(message, self.strings("kick_none", message))
        if not user:
            return

        try:
            await self.client.kick_participant(message.chat_id, user.id)
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))

        await self.allmodules.log("kick", group=message.chat_id, affected_uids=[user.id])
        await utils.answer(message, self.strings("kicked", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    @loader.ratelimit
    async def promotecmd(self, message):
        """Дать админку"""
        args = utils.get_args(message)
        user = await self._get_user(message, self.strings("promote_none", message))
        if not user:
            return

        rank = ' '.join(args[1:]) if len(args) > 1 else ""

        rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=False,
            manage_call=True,
            anonymous=False,
        )

        try:
            await self.client(EditAdminRequest(message.chat_id, user.id, rights, rank))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))

        await self.allmodules.log("promote", group=message.chat_id, affected_uids=[user.id])
        await utils.answer(message, self.strings("promoted", message).format(utils.escape_html(user.first_name), user.id))

    @loader.group_admin_add_admins
    async def demotecmd(self, message):
        """Снять админку"""
        user = await self._get_user(message, self.strings("demote_none", message))
        if not user:
            return

        try:
            if message.is_channel:
                rights = ChatAdminRights(
                    change_info=False,
                    post_messages=False,
                    edit_messages=False,
                    delete_messages=False,
                    ban_users=False,
                    invite_users=False,
                    pin_messages=False,
                    add_admins=False,
                    manage_call=False,
                    anonymous=False,
                )
                await self.client(EditAdminRequest(message.chat_id, user.id, rights, ""))
            else:
                await self.client(EditChatAdminRequest(message.chat_id, user.id, False))
        except BadRequestError:
            return await utils.answer(message, self.strings("not_admin", message))

        await self.allmodules.log("demote", group=message.chat_id, affected_uids=[user.id])
        await utils.answer(message, self.strings("demoted", message).format(utils.escape_html(user.first_name), user.id))

    async def _get_user(self, message, empty_error_text):
        if message.is_reply:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, empty_error_text)
                return None
            return await utils.get_user(reply)

        args = utils.get_args(message)
        if not args:
            await utils.answer(message, empty_error_text)
            return None

        who = int(args[0]) if args[0].isdigit() else args[0]
        try:
            return await self.client.get_entity(who)
        except Exception:
            await utils.answer(message, self.strings("who", message))
            return None
