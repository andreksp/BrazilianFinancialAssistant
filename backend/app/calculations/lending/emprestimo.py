"""
Calculation module for Empréstimo de Ações (securities lending / BTC-CBLC) — Phase 3.

Business Logic Reference: backend/data/regulations/ir_emprestimo_acoes.txt
- A remuneração recebida pelo DOADOR é tributada como aplicação de renda fixa,
  pela tabela regressiva por prazo do contrato (não pelas regras de renda variável
  de ações — 15%/20% + isenção de R$20.000 NÃO se aplicam aqui):
    até 180 dias ...... 22,5%
    181 a 360 dias ..... 20,0%
    361 a 720 dias ..... 17,5%
    acima de 720 dias .. 15,0%
- O IR é retido na fonte pela B3/CBLC e é definitivo (tributação exclusiva) —
  não gera DARF mensal adicional para o investidor.
- Base legal: Lei nº 15.265/2025 (dispõe especificamente sobre a tributação do
  empréstimo de títulos e valores mobiliários no País); Lei 13.043/2014 (base
  histórica); Instrução Normativa RFB 1.585/2015.

Modeling note: este é um evento de renda (remuneração recebida), não uma compra/venda
de ativo com preço médio. `quantidade` = nº de ações emprestadas, `preco_unitario` =
remuneração por ação (R$), e `prazo_dias` (campo opcional em TradeInput) define a faixa
da tabela regressiva. `prazo_dias` é OBRIGATÓRIO nesta versão: presumir uma faixa sem
confirmação do usuário poderia subestimar ou superestimar o IR retido, então o cálculo
recusa a operação (ValueError) em vez de adivinhar.
"""

from typing import Optional

from app.models.trade import (
    TradeInput,
    TradeOperationType,
    TaxCalculationResult,
    AssetType,
    FeesBreakdown,
)
from app.calculations.base import BaseCalculator

DEFAULT_PRAZO_DIAS = 180  # conservative fallback when the contract term isn't informed

_REGRESSIVE_BRACKETS = (
    (180, 0.225),
    (360, 0.20),
    (720, 0.175),
    (float("inf"), 0.15),
)


def _zero_fees() -> FeesBreakdown:
    """Empréstimo de ações não tem a mesma estrutura de taxas B3 de compra/venda."""
    return FeesBreakdown(
        taxa_liquidacao=0.0,
        taxa_registro=0.0,
        emolumentos=0.0,
        corretagem=0.0,
        iss_sobre_corretagem=0.0,
    )


class EmprestimoCalculator(BaseCalculator):
    """Calculator for the lender's (doador's) rental income from Empréstimo de Ações."""

    def get_regressive_rate(self, prazo_dias: Optional[int]) -> float:
        dias = prazo_dias or DEFAULT_PRAZO_DIAS
        for limite, aliquota in _REGRESSIVE_BRACKETS:
            if dias <= limite:
                return aliquota
        return _REGRESSIVE_BRACKETS[-1][1]

    def calculate_gain_loss(
        self, quantity: float, purchase_price: float, sale_price: float
    ) -> float:
        """Não há custo de aquisição: o ganho é a remuneração bruta recebida."""
        return quantity * sale_price

    def get_tax_rate(self, is_day_trade: bool = False, prazo_dias: Optional[int] = None) -> float:
        return self.get_regressive_rate(prazo_dias)

    def get_irrf_rate(self, is_day_trade: bool = False, prazo_dias: Optional[int] = None) -> float:
        # Tributação exclusiva na fonte: a alíquota regressiva JÁ É o IRRF definitivo.
        return self.get_regressive_rate(prazo_dias)

    def calculate_result(
        self, trade: TradeInput, average_price: Optional[float] = None
    ) -> TaxCalculationResult:
        assert trade.tipo_ativo == AssetType.EMPRESTIMO_ACOES, "This calculator is for Empréstimo de Ações only"

        if trade.prazo_dias is None:
            raise ValueError("Informe o prazo do contrato para determinar a faixa de IRRF.")
        valor_financeiro = trade.quantidade * trade.preco_unitario
        aliquota = self.get_regressive_rate(trade.prazo_dias)

        # Tributação exclusiva na fonte: já é o valor final retido, sem DARF adicional.
        irrf_retido = valor_financeiro * aliquota
        ir_devido = 0.0

        ganho_liquido = valor_financeiro - irrf_retido
        valor_liquido = ganho_liquido

        return TaxCalculationResult(
            ativo=trade.ativo,
            tipo_ativo=trade.tipo_ativo,
            quantidade=trade.quantidade,
            preco_unitario=trade.preco_unitario,
            data_operacao=trade.data_operacao,
            valor_financeiro=valor_financeiro,
            ganho_prejuizo_bruto=valor_financeiro,
            taxas_totais=_zero_fees(),
            aliquota_aplicada=aliquota,
            ir_devido=ir_devido,
            irrf_retido=irrf_retido,
            isenção_aplicada=False,
            ganho_prejuizo_liquido=ganho_liquido,
            valor_liquido=valor_liquido,
            tipo_operacao_classificacao=TradeOperationType.SWING,
            mensagem=self._generate_message(trade, valor_financeiro, aliquota, irrf_retido),
        )

    def _generate_message(
        self, trade: TradeInput, valor_financeiro: float, aliquota: float, irrf_retido: float
    ) -> str:
        def fmt(v: float) -> str:
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # trade.prazo_dias é garantido não-nulo por calculate_result antes de chegar aqui.
        return (
            f"Aluguel de {int(trade.quantidade)} {trade.ativo}: remuneração bruta {fmt(valor_financeiro)}. "
            f"Prazo do contrato: {trade.prazo_dias} dias. "
            f"IR retido na fonte (definitivo, tabela regressiva {aliquota * 100:.1f}%): {fmt(irrf_retido)}. "
            "Tributação exclusiva — não gera DARF mensal."
        )
