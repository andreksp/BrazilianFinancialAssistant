"""Conservative, host-controlled chat persistence and read-only clarification."""
import logging
import re
import unicodedata
from datetime import date

log = logging.getLogger(__name__)


def normalized(message):
    return ''.join(c for c in unicodedata.normalize('NFKD', message.lower())
                   if not unicodedata.combining(c))


def may_register(message, trade):
    """An extracted trade alone never authorizes a write to the portfolio."""
    text = normalized(message).strip()
    if trade.data_operacao > date.today():
        return False
    if re.search(r'\b(se|caso|simul\w*|hipot\w*|exemplo|supon\w*|venderia|compraria|pretendo|penso|vou|quero)\b', text):
        return False
    if re.search(r'\bnao\b.{0,40}\b(registr\w*|grav\w*|salv\w*|vendi|comprei|realizei|houve)\b', text):
        return False
    # Narrow affirmative syntax. Unclear intent remains read-only.
    return bool(re.match(
        r'^(?:eu\s+)?(?:ja\s+)?(?:comprei|vendi|adquiri|aluguei|'
        r'registre|registrar|registre\s+agora)\b', text))


def history_clarification(message, lookup):
    """Look up one explicitly named asset, even without a complete TradeInput.

    No model-provided identity or invented quantity, price or tax enters this path.
    Multiple assets require clarification rather than an arbitrary selection.
    """
    text = normalized(message)
    operation = bool(re.search(r'\b(vend\w*|compr\w*|simul\w*)\b', text))
    history = bool(re.search(r'preco medio|custo medio|historico|carteira|saldo', text))
    if not (operation or history):
        return None
    assets = set(re.findall(r'\b[A-Z]{4}[A-Z]?\d{1,3}\b', message.upper()))
    assets.update(re.findall(r'\b(?:BTC|ETH|SOL|USDT|USDC|WIN|WDO)\b', message.upper()))
    if len(assets) != 1:
        return None
    asset = next(iter(assets))
    cost = lookup(asset)
    log.info('chat_history_lookup asset=%s status=%s mode=read_only',
             asset, 'found' if cost is not None else 'unavailable')
    if cost is None:
        answer = (f'Não encontrei preço médio disponível para {asset} no seu saldo atual. '
                  'Compras antigas podem existir mesmo quando as vendas já zeraram o saldo. '
                  'Confira o histórico ou informe o custo médio de aquisição.')
    else:
        value = f'{cost:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        answer = (f'Consultei seu histórico: o preço médio atual de {asset} é R$ {value} por unidade. '
                  'Esse valor considera as operações registradas e não certifica o custo de uma data passada.')
    if operation:
        answer += ('\n\nAinda não foi possível validar todos os dados da operação. '
                   'Reenvie a mensagem completa com quantidade de ações/cotas/unidades, '
                   'preço por unidade, data e modalidade (operação comum ou day trade). '
                   'Exemplo de formato: "Simule a venda de 100 ações de PETR4 por R$ 51,00 cada '
                   'em 02/10/2026, operação comum". '
                   'O chat não mantém o contexto entre mensagens.')
        if cost is not None:
            answer += ' Não é necessário repetir o preço médio: ele poderá ser consultado novamente.'
    return answer + '\n\nNenhuma operação foi registrada e nenhum imposto foi calculado nesta consulta.'
