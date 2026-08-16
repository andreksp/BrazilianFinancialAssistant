/**
 * Trade Input Component (Phase 4).
 *
 * Structured form for inputting trade details.
 *
 * Features:
 * - Asset dropdown (PETR4, VALE3, etc)
 * - Operation type (buy/sell)
 * - Quantity and price inputs
 * - Date picker (PT-BR format)
 * - Broker selection
 * - Fee inputs (percentage or fixed)
 * - Calculate button
 */

import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TradeInput, TaxCalculationResult } from '../../models/trade';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-trade-input',
  templateUrl: './trade-input.component.html',
  styleUrls: ['./trade-input.component.css'],
})
export class TradeInputComponent implements OnInit {
  tradeForm: FormGroup;
  loading: boolean = false;
  calculationResult: TaxCalculationResult | null = null;
  buyConfirmation: string | null = null;
  error: string | null = null;

  // Dropdown options
  assetTypes = ['acao', 'bdr', 'fii', 'opcao'];
  operationTypes = ['compra', 'venda'];
  brokers = ['C6', 'XP', 'Clear', 'Nubank', 'Bradesco', 'Outro'];

  constructor(
    private formBuilder: FormBuilder,
    private apiService: ApiService
  ) {
    this.tradeForm = this.formBuilder.group({
      ativo: ['', [Validators.required, Validators.minLength(4)]],
      tipo_ativo: ['acao', Validators.required],
      tipo_operacao: ['venda', Validators.required],
      quantidade: [
        '',
        [Validators.required, Validators.min(0.01)],
      ],
      preco_unitario: [
        '',
        [Validators.required, Validators.min(0.01)],
      ],
      data_operacao: ['', Validators.required],
      corretora: [''],
      corretagem_percentual: [0.001, [Validators.min(0), Validators.max(1)]],
      corretagem_fixa: [0, [Validators.min(0)]],
      nota: [''],
    });
  }

  ngOnInit(): void {
    // Initialize form with today's date
    const today = new Date().toISOString().split('T')[0];
    this.tradeForm.patchValue({
      data_operacao: today,
    });
  }

  /**
   * Submit trade for calculation.
   */
  onSubmit(): void {
    if (this.tradeForm.invalid) {
      this.error = 'Por favor, preencha todos os campos obrigatórios.';
      return;
    }

    this.loading = true;
    this.error = null;
    this.calculationResult = null;
    this.buyConfirmation = null;

    const formValue = this.tradeForm.value;
    const trade: TradeInput = {
      ativo: formValue.ativo.toUpperCase(),
      tipo_ativo: formValue.tipo_ativo,
      tipo_operacao: formValue.tipo_operacao,
      quantidade: parseFloat(formValue.quantidade),
      preco_unitario: parseFloat(formValue.preco_unitario),
      data_operacao: new Date(formValue.data_operacao),
      corretora: formValue.corretora || undefined,
      corretagem_percentual: parseFloat(formValue.corretagem_percentual),
      corretagem_fixa: parseFloat(formValue.corretagem_fixa),
      nota: formValue.nota || undefined,
    };

    this.apiService.processTrade(trade).subscribe({
      next: (result: any) => {
        if (result.tipo_operacao === 'compra') {
          this.buyConfirmation = result.mensagem || `Compra de ${result.ativo} registrada com sucesso.`;
        } else {
          this.calculationResult = result as TaxCalculationResult;
        }
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error processing trade:', error);
        this.error = error.error?.detail || 'Erro ao processar a operação.';
        this.loading = false;
      },
    });
  }

  /**
   * Reset form to empty state.
   */
  resetForm(): void {
    this.tradeForm.reset();
    this.calculationResult = null;
    this.buyConfirmation = null;
    this.error = null;
    const today = new Date().toISOString().split('T')[0];
    this.tradeForm.patchValue({
      data_operacao: today,
      tipo_ativo: 'acao',
      tipo_operacao: 'venda',
    });
  }

  /**
   * Format number as Brazilian currency.
   */
  formatCurrency(value: number): string {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
  }
}
