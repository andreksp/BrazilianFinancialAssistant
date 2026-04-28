/**
 * TypeScript interfaces for trade data (Phase 4 - Angular).
 *
 * Reference: backend/app/models/trade.py for Pydantic models
 */

export type AssetType = 'acao' | 'bdr' | 'fii' | 'opcao' | 'futuro_dolar' | 'futuro_indice';
export type OperationType = 'compra' | 'venda';
export type TradeOperationType = 'swing' | 'day_trade';

/**
 * Trade input model.
 *
 * Business Logic:
 * - Preço médio: Weighted average of all purchases
 * - Classificação: Swing vs day trade affects tax rate
 * - Corretagem: Can be percentage or fixed
 */
export interface TradeInput {
  ativo: string;
  tipo_ativo: AssetType;
  tipo_operacao: OperationType;
  quantidade: number;
  preco_unitario: number;
  data_operacao: Date;
  corretora?: string;
  corretagem_percentual?: number;
  corretagem_fixa?: number;
  nota?: string;
}

/**
 * Fee breakdown from a trade.
 *
 * Reference: research.md section 2
 * - Taxa de liquidação: 0,0275%
 * - Taxa de registro: 0,0034%
 * - Emolumentos: 0,003%
 * - ISS: 5% on corretagem
 */
export interface FeesBreakdown {
  taxa_liquidacao: number;
  taxa_registro: number;
  emolumentos: number;
  corretagem: number;
  iss_sobre_corretagem: number;
}

/**
 * Complete calculation result for a trade.
 *
 * Business Logic (research.md):
 * - IR: 15% (swing) or 20% (day trade)
 * - Isenção: R$20.000/month for swing trades
 * - IRRF: 0,005% (swing) or 1% (day trade)
 */
export interface TaxCalculationResult {
  ativo: string;
  tipo_ativo: AssetType;
  quantidade: number;
  preco_unitario: number;
  data_operacao: Date;
  valor_financeiro: number;
  ganho_prejuizo_bruto: number;
  taxas_totais: FeesBreakdown;
  aliquota_aplicada: number;
  ir_devido: number;
  irrf_retido: number;
  isenção_aplicada: boolean;
  ganho_prejuizo_liquido: number;
  valor_liquido: number;
  tipo_operacao_classificacao: TradeOperationType;
  mensagem?: string;
}

/**
 * Monthly tax summary for DARF.
 *
 * Reference: research.md section 5
 * - DARF code: 6015 (Pessoa Física)
 * - Due date: Last business day of following month
 * - Minimum: R$10,00
 */
export interface MonthlyTaxSummary {
  mes: number;
  ano: number;
  ganho_swing_trade: number;
  prejuizo_swing_trade: number;
  ganho_day_trade: number;
  prejuizo_day_trade: number;
  ir_swing_trade: number;
  ir_day_trade: number;
  irrf_retido_total: number;
  ir_total_devido: number;
  darf_vencimento: Date;
}

/**
 * Chat message.
 */
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  trade_extracted?: TradeInput;
  calculation_result?: TaxCalculationResult;
}

export interface ChatRequest {
  message: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  trade_extracted?: TradeInput;
  calculation_result?: TaxCalculationResult;
  confidence: number;
}
