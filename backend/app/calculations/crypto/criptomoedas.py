"""
Calculation module for Criptomoedas (Bitcoin, altcoins, stablecoins).

Business Logic Reference: Documentation/research.md section 9 /
backend/data/regulations/ir_cripto.txt

CRITICAL RULES (regime nacional — exchange brasileira):
- Ganho de capital apurado via GCAP (não pela regra de renda variável de ações)
- Isenção: vendas totais do mês (todas as criptomoedas, todas as exchanges
  nacionais somadas) até R$35.000,00 — Instrução Normativa SRF 84/2001, art. 3º, IX
- Acima disso, tabela progressiva de ganho de capital (Lei 13.259/2016):
  15% até R$5.000.000, 17,5% de R$5-10M, 20% de R$10-30M, 22,5% acima de R$30M
- Sem distinção day trade / swing trade (diferente de ações)
- Sem IRRF "dedo-duro" (não há intermediação B3)
- DARF código 4600, vencimento no último dia útil do mês seguinte

CRITICAL RULES (regime exterior — exchange estrangeira / autocustódia fora do país):
- Lei 14.754/2023: tratado como "aplicação financeira no exterior"
- Alíquota fixa de 15% sobre o ganho líquido anual, SEM isenção de R$35.000
- Apuração e recolhimento na Declaração de Ajuste Anual (DAA), não por DARF mensal

LIMITATION (MVP): a isenção de R$35.000 e a alíquota progressiva são aplicadas
por operação (valor_financeiro / ganho da própria venda), não pela soma real de
todas as vendas de criptoativos do usuário no mês em todas as exchanges
nacionais, como a regra realmente exige. A agregação mensal correta depende de
um cálculo em nível de carteira/mês, ainda não implementado no TaxEngine (o
mesmo TODO já existe para a isenção de R$20.000 de ações — ver acoes.py).
"""

from typing import List, Optional, Tuple

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    AssetType,
)
from app.calculations.base import BaseCalculator
from app.calculations.fees.crypto_fees import calculate_crypto_fees


class CriptomoedaCalculator(BaseCalculator):
    """
    Calculator for Criptomoedas trades.

    Tax Rules (from ir_cripto.txt):
    - Regime nacional: isenção R$35.000/mês + tabela progressiva 15%-22,5%
    - Regime exterior (Lei 14.754/2023): 15% fixo, sem isenção
    - Sem IRRF, sem distinção swing/day trade
    """

    NATIONAL_EXEMPTION_LIMIT = 35000.0  # R$35,000/month, national exchanges
    FOREIGN_FLAT_RATE = 0.15  # Lei 14.754/2023 — ativos no exterior

    # Progressive capital-gains table (Lei 13.259/2016), upper limit -> rate
    PROGRESSIVE_BRACKETS: List[Tuple[float, float]] = [
        (5_000_000.0, 0.15),
        (10_000_000.0, 0.175),
        (30_000_000.0, 0.20),
        (float("inf"), 0.225),
    ]

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """Ganho = (preço de venda - preço médio) × quantidade."""
        return (sale_price - purchase_price) * quantity

    def get_progressive_rate(self, ganho: float) -> float:
        """Return the marginal rate for a given (monthly) capital gain."""
        for limite, aliquota in self.PROGRESSIVE_BRACKETS:
            if ganho <= limite:
                return aliquota
        return self.PROGRESSIVE_BRACKETS[-1][1]

    def get_tax_rate(self, is_day_trade: bool = False) -> float:
        """
        Base rate for the calculator interface. Crypto has no day-trade split;
        actual rate depends on regime (nacional progressivo / exterior 15% fixo)
        and is resolved in calculate_result via get_progressive_rate.
        """
        return self.PROGRESSIVE_BRACKETS[0][1]

    def progressive_tax(self, gain: float) -> float:
        """Aplica cada alíquota somente à parcela da respectiva faixa."""
        total, lower = 0.0, 0.0
        for upper, rate in self.PROGRESSIVE_BRACKETS:
            total += max(0.0, min(gain, upper) - lower) * rate
            lower = upper
        return round(total, 2)

    def get_irrf_rate(self, is_day_trade: bool = False) -> float:
        """Crypto sales have no B3-style withholding (dedo-duro)."""
        return 0.0

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        """Calculate complete tax and fee result for a crypto trade."""
        assert trade.tipo_ativo == AssetType.CRIPTO, "This calculator is for Criptomoedas only"
        assert trade.tipo_operacao.value == "venda", "This calculator only handles sales"

        valor_financeiro = trade.quantidade * trade.preco_unitario
        if average_price is None:
            raise ValueError("Informe o custo médio de aquisição; não é seguro presumir ganho zero.")
        if trade.exchange_estrangeira:
            raise ValueError("Ativo no exterior exige apuração anual e enquadramento fiscal; este cálculo cobre somente o regime nacional.")
        if trade.total_vendas_mes is None or trade.total_vendas_mes < valor_financeiro:
            raise ValueError("Informe o total completo das alienações nacionais de criptoativos no mês, incluindo esta operação.")
        pm = average_price
        ganho_bruto = self.calculate_gain_loss(trade.quantidade, pm, trade.preco_unitario)

        fees = calculate_crypto_fees(valor_financeiro, trade)

        exterior = trade.exchange_estrangeira
        isencao_aplicada = False

        if exterior:
            aliquota = self.FOREIGN_FLAT_RATE
            ir_devido = max(0, ganho_bruto) * aliquota
        elif trade.total_vendas_mes <= self.NATIONAL_EXEMPTION_LIMIT:
            aliquota = 0.0
            ir_devido = 0.0
            isencao_aplicada = True
        else:
            base = max(0, ganho_bruto - fees.total)
            ir_devido = self.progressive_tax(base)
            aliquota = ir_devido / base if base else 0.0

        irrf_retido = self.get_irrf_rate()

        ganho_liquido = ganho_bruto - fees.total
        valor_liquido = valor_financeiro - fees.total - ir_devido - irrf_retido

        result = TaxCalculationResult(
            ativo=trade.ativo,
            tipo_ativo=trade.tipo_ativo,
            quantidade=trade.quantidade,
            preco_unitario=trade.preco_unitario,
            data_operacao=trade.data_operacao,
            valor_financeiro=valor_financeiro,
            ganho_prejuizo_bruto=ganho_bruto,
            taxas_totais=fees,
            aliquota_aplicada=aliquota,
            ir_devido=ir_devido,
            irrf_retido=irrf_retido,
            isenção_aplicada=isencao_aplicada,
            ganho_prejuizo_liquido=ganho_liquido,
            valor_liquido=valor_liquido,
            # Crypto has no swing/day-trade split; SWING is used here only to
            # satisfy the shared schema field, not as a tax classification.
            tipo_operacao_classificacao=TradeOperationType.SWING,
            mensagem=self._generate_message(trade, ganho_bruto, ir_devido, isencao_aplicada, exterior, aliquota),
        )

        return result

    def _generate_message(
        self,
        trade: TradeInput,
        ganho_bruto: float,
        ir_devido: float,
        isencao: bool,
        exterior: bool,
        aliquota: float,
    ) -> str:
        """Generate user-friendly summary message."""
        ganho_str = f"R$ {ganho_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        regime = "exchange estrangeira" if exterior else "exchange nacional"

        msg = f"Venda de {trade.ativo} ({regime}): {ganho_str}"

        if isencao:
            msg += " (isenção de R$ 35.000/mês aplicada — sem IR)"
        elif ir_devido > 0:
            ir_str = f"R$ {ir_devido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            msg += f" - IR devido ({aliquota * 100:.1f}%): {ir_str}"

        return msg
