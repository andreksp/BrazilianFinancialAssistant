/**
 * Results Component (Phase 4).
 *
 * Displays calculation results with:
 * - Gain/loss summary
 * - Fee breakdown
 * - Tax calculation (IR)
 * - IRRF withheld
 * - Net value received
 *
 * Formatting:
 * - PT-BR locale (R$, vírgula decimal)
 * - DD/MM/YYYY dates
 * - 2 decimal places for currency
 */

import { Component, Input } from '@angular/core';
import { TaxCalculationResult, FeesBreakdown } from '../../models/trade';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css'],
})
export class ResultsComponent {
  @Input() result: TaxCalculationResult | null = null;

  /**
   * Format number as Brazilian currency (R$ format with comma decimal).
   */
  formatCurrency(value: number): string {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
  }

  /**
   * Format date as DD/MM/YYYY.
   */
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('pt-BR');
  }

  /**
   * Format percentage with 2 decimals.
   */
  formatPercent(value: number): string {
    return (value * 100).toFixed(2) + '%';
  }

  /**
   * Get CSS class for gain/loss (green for gain, red for loss).
   */
  getGainLossClass(): string {
    if (!this.result) return '';
    return this.result.ganho_prejuizo_bruto >= 0 ? 'gain' : 'loss';
  }

  /**
   * Get CSS class for tax (important if > R$100).
   */
  getTaxClass(): string {
    if (!this.result) return '';
    return this.result.ir_devido > 100 ? 'highlight' : '';
  }

  /**
   * Calculate total fees from breakdown.
   */
  getTotalFees(): number {
    if (!this.result || !this.result.taxas_totais) return 0;
    const fees = this.result.taxas_totais;
    return (fees.taxa_liquidacao || 0) + (fees.taxa_registro || 0) +
           (fees.emolumentos || 0) + (fees.corretagem || 0) + (fees.iss_sobre_corretagem || 0);
  }
}
