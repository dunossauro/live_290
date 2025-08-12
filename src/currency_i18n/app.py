import json
import locale
import urllib.request
from argparse import ArgumentParser
from datetime import datetime
from decimal import Decimal
from gettext import translation

localization, encode = locale.getlocale()

t = translation('messages', localedir='locale', fallback=True)
t.install(f'{localization}{encode}')
_ = t.gettext


# Definição do CLI para escolher as moedas
cli = ArgumentParser(
    description=_('BRL currency'),
    epilog=_('Basic example of l10n'),
)

cli.add_argument(
    '--currency',
    '-c',
    choices=['BTC', 'USD', 'EUR'],
    type=str,
    help=_('Reference currency for BRL comparison'),
    required=True,
    action='append',
)

cli.add_argument(
    '--language',
    '-l',
    choices=['pt_BR', 'en_US', 'eo'],
    type=str,
    default=localization,
    required=True,
    help=_('Prefered language fo the answer')
)

args = cli.parse_args()

if args.language != localization:
    # TODO: Arrumar um lugar melhor pra essa lógica
    locale.setlocale(locale.LC_ALL, f'{args.language}.{encode}')
    t = translation(
        'messages',
        localedir='locale',
        fallback=True,
        languages=[args.language]
    )
    t.install()
    _ = t.gettext

    

# Requisição web para pegar os dados da cotação
currencies = ','.join(f'{c}-BRL' for c in args.currency)
url = f'https://economia.awesomeapi.com.br/json/last/{currencies}'

with urllib.request.urlopen(url) as response:
    response_data = response.read().decode('UTF-8')
    response_json = json.loads(response_data)


# Tratamento e apresentação dos dados de saída
cl = len(args.currency)

print(
    t.ngettext(
        'Requested %(currencies)s currency for comparison against BRL',
	'Requested %(cl)s currencies for comparison against BRL: %(currencies)s',
        cl,
    ) % {'cl': cl, 'currencies': args.currency}
)


for currency in sorted(args.currency, key=locale.strxfrm):
    currency_data = response_json.get(f'{currency}BRL')
    trade_time = datetime.fromtimestamp(int(currency_data['timestamp']))

    if cl > 1:
        print(f'\n{currency}')

    print(
        _('Last trade: {trade_time}').format(
            trade_time=datetime.strftime(
                trade_time, locale.nl_langinfo(locale.D_T_FMT)
            )
        )
    )
    print(_('Bid price: {price}').format(
        price=locale.currency(
            Decimal(currency_data['bid']),
            grouping=True,
        )
    ))
    print(_('Ask price: {price}').format(
        price=locale.currency(
            Decimal(currency_data['ask']),
            grouping=True,
        )
    ))
    print(_('Price variation: {price}').format(
        price=locale.currency(
            Decimal(currency_data['varBid']),
            grouping=True,
        )
    ))
