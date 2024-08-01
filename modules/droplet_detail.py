from telebot.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import digitalocean

from _bot import bot
from utils.db import AccountsDB
from utils.localizer import localize_region


def droplet_detail(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]
    droplet_id = data['droplet_id'][0]
    t = '<b>details server</b>\n\n'

    account = AccountsDB().get(doc_id=doc_id)

    bot.edit_message_text(
        text=f'{t}'
             f'akun: <code>{account["email"]}</code>\n\n'
             'Get instance information...',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML'
    )

    droplet = digitalocean.Droplet().get_object(
        api_token=account['token'],
        droplet_id=droplet_id
    )

    markup = InlineKeyboardMarkup()
    markup.row(

        InlineKeyboardButton(
            text='Delete',
            callback_data=f'droplet_actions?doc_id={doc_id}&droplet_id={droplet_id}&a=delete'
        ),
    )
    power_buttons = []
    if droplet.status == 'active':
        power_buttons.extend([
            InlineKeyboardButton(
                text='Shut down',
                callback_data=f'droplet_actions?doc_id={doc_id}&droplet_id={droplet_id}&a=shutdown'
            ),
            InlineKeyboardButton(
                text='Reboot',
                callback_data=f'droplet_actions?doc_id={doc_id}&droplet_id={droplet_id}&a=reboot'
            )
        ])
    else:
        power_buttons.append(
            InlineKeyboardButton(
                text='Power On',
                callback_data=f'droplet_actions?doc_id={doc_id}&droplet_id={droplet_id}&a=power_on'
            )
        )
    markup.row(*power_buttons)
    markup.row(
        InlineKeyboardButton(
            text='Refresh',
            callback_data=f'droplet_detail?doc_id={account.doc_id}&droplet_id={droplet_id}'
        ),
        InlineKeyboardButton(
            text='Back',
            callback_data=f'list_droplets?doc_id={account.doc_id}'
        )
    )

    bot.edit_message_text(
        text=f'{t}'
             f'Acc: <code>{account["email"]}</code>\n'
             f'Name: <code>{droplet.name}</code>\n'
             f'Model: <code>{droplet.size_slug}</code>\n'
             f'Country: <code>{localize_region(droplet.region["slug"])}</code>\n'
             f'Os sys: <code>{droplet.image["distribution"]} {droplet.image["name"]}</code>\n'
             f'Hard disk: <code>{droplet.disk} GB</code>\n'
             f'Server IP: <code>{droplet.ip_address}</code>\n'
             f'Private IP： <code>{droplet.private_ip_address}</code>\n'
             f'Status: <code>{droplet.status}</code>\n'
             f'StartDate: <code>{droplet.created_at.split("T")[0]}</code>\n',
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        parse_mode='HTML',
        reply_markup=markup
    )
