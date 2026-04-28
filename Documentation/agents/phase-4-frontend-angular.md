# Agent: Phase 4 — Frontend Angular

**Responsabilidade**: Interface web para usuários (chat + formulário estruturado)  
**Duração**: 5-7 dias  
**Input**: Phase 2-3 (API endpoints completo)  
**Output**: App Angular rodando em localhost:4200  

---

## Conhecimento de Negócio

### User Workflows

#### Workflow 1: Chat Natural Language (Ideal, requer Phase 3)
1. Usuário digita: "Vendi 100 PETR4 a R$25,50 hoje"
2. Backend extrai trade com LLM
3. Calcula IR, taxas
4. Retorna explicação em português
5. Usuário vê resultado + mensagem clara

#### Workflow 2: Structured Form (Fallback, sempre disponível)
1. Usuário preenche formulário:
   - Ativo: PETR4
   - Operação: Venda
   - Quantidade: 100
   - Preço: 25,50
   - Data: 15/03/2025
2. Clica "Calcular"
3. Mesmo resultado que chat, mas entrada estruturada

**MVP**: Implementar apenas Workflow 2 (formulário). Workflow 1 é nice-to-have Phase 3.

### Locale PT-BR

Brasileiros esperam:
- **Moeda**: R$ 2.550,50 (vírgula para decimal, ponto para milhares)
- **Datas**: 15/03/2025 (DD/MM/YYYY)
- **Números**: 1.234,56 (mil ponto, décimal vírgula)
- **Texto**: Português do Brasil

---

## Architecture: Component Hierarchy

```
app-root (AppComponent)
├── Navigation/Header
├── Main Content
│   ├── TabGroup
│   │   ├── Tab 1: Chat (ChatComponent)
│   │   ├── Tab 2: Formulário (TradeInputComponent)
│   │   ├── Tab 3: Resumo (SummaryComponent)
│   │   └── Tab 4: Histórico (HistoryComponent)
│   ├── Results Panel (ResultsComponent)
│   └── Footer
└── Services
    └── ApiService (HTTP calls)
```

---

## Tarefas de Implementação

### 1. Setup Angular 17
```bash
ng new brazilian-financial-assistant --standalone
cd brazilian-financial-assistant
npm install @angular/material
```

**Key Features Angular 17**:
- Standalone components (sem modules)
- Signals para reatividade (mais simples que RxJS)
- Control flow syntax (@if, @for, @switch)
- Dependency injection otimizado

### 2. Modelos TypeScript
**Arquivo**: `src/app/models/trade.ts`

```typescript
export type AssetType = 'acao' | 'bdr' | 'fii' | 'opcao';
export type OperationType = 'compra' | 'venda';
export type TradeOperationType = 'swing' | 'day_trade';

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
}

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

export interface FeesBreakdown {
  taxa_liquidacao: number;
  taxa_registro: number;
  emolumentos: number;
  corretagem: number;
  iss_sobre_corretagem: number;
}
```

### 3. API Service
**Arquivo**: `src/app/services/api.service.ts`

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  TradeInput,
  TaxCalculationResult,
  ChatRequest,
  ChatResponse,
  MonthlyTaxSummary,
} from '../models/trade';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = '/api';

  constructor(private http: HttpClient) {}

  processTrade(trade: TradeInput): Observable<TaxCalculationResult> {
    return this.http.post<TaxCalculationResult>(
      `${this.apiUrl}/trades/process`,
      trade
    );
  }

  sendChat(message: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(
      `${this.apiUrl}/chat/message`,
      { message }
    );
  }

  getMonthlySummary(month: number, year: number): Observable<MonthlyTaxSummary> {
    const params = new HttpParams()
      .set('month', month)
      .set('year', year);

    return this.http.get<MonthlyTaxSummary>(
      `${this.apiUrl}/calculations/summary`,
      { params }
    );
  }
}
```

### 4. Trade Input Component (Formulário Estruturado)
**Arquivo**: `src/app/components/trade-input/trade-input.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TradeInput, TaxCalculationResult } from '../../models/trade';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-trade-input',
  templateUrl: './trade-input.component.html',
  styleUrls: ['./trade-input.component.css'],
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, MatFormFieldModule, MatInputModule, MatButtonModule],
})
export class TradeInputComponent implements OnInit {
  tradeForm: FormGroup;
  loading = false;
  calculationResult: TaxCalculationResult | null = null;
  error: string | null = null;

  assetTypes = ['acao', 'bdr', 'fii', 'opcao'];
  operationTypes = ['compra', 'venda'];
  brokers = ['C6', 'XP', 'Clear', 'Nubank', 'Bradesco'];

  constructor(
    private formBuilder: FormBuilder,
    private apiService: ApiService
  ) {
    this.tradeForm = this.formBuilder.group({
      ativo: ['', [Validators.required, Validators.minLength(4)]],
      tipo_ativo: ['acao', Validators.required],
      tipo_operacao: ['venda', Validators.required],
      quantidade: ['', [Validators.required, Validators.min(0.01)]],
      preco_unitario: ['', [Validators.required, Validators.min(0.01)]],
      data_operacao: ['', Validators.required],
      corretora: [''],
      corretagem_percentual: [0.001],
      corretagem_fixa: [0],
    });
  }

  ngOnInit(): void {
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    this.tradeForm.patchValue({ data_operacao: today });
  }

  onSubmit(): void {
    if (this.tradeForm.invalid) {
      this.error = 'Por favor, preencha todos os campos obrigatórios.';
      return;
    }

    this.loading = true;
    this.error = null;

    const formValue = this.tradeForm.value;
    const trade: TradeInput = {
      ativo: formValue.ativo.toUpperCase(),
      tipo_ativo: formValue.tipo_ativo,
      tipo_operacao: formValue.tipo_operacao,
      quantidade: parseFloat(formValue.quantidade),
      preco_unitario: parseFloat(formValue.preco_unitario),
      data_operacao: new Date(formValue.data_operacao),
      corretora: formValue.corretora || undefined,
      corretagem_percentual: parseFloat(formValue.corretagem_percentual || 0),
      corretagem_fixa: parseFloat(formValue.corretagem_fixa || 0),
    };

    this.apiService.processTrade(trade).subscribe({
      next: (result: TaxCalculationResult) => {
        this.calculationResult = result;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        this.error = error.error?.detail || 'Erro ao processar.';
        this.loading = false;
      },
    });
  }

  resetForm(): void {
    this.tradeForm.reset();
    this.calculationResult = null;
    this.error = null;
  }
}
```

**HTML** (`trade-input.component.html`):
```html
<mat-card class="form-card">
  <mat-card-header>
    <mat-card-title>Inserir Operação</mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <form [formGroup]="tradeForm" (ngSubmit)="onSubmit()">
      <mat-form-field appearance="outline">
        <mat-label>Ativo (ex: PETR4)</mat-label>
        <input matInput formControlName="ativo" />
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Tipo</mat-label>
        <mat-select formControlName="tipo_ativo">
          <mat-option *ngFor="let type of assetTypes" [value]="type">
            {{ type }}
          </mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Operação</mat-label>
        <mat-select formControlName="tipo_operacao">
          <mat-option *ngFor="let op of operationTypes" [value]="op">
            {{ op }}
          </mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Quantidade</mat-label>
        <input matInput type="number" formControlName="quantidade" />
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Preço Unitário</mat-label>
        <input matInput type="number" formControlName="preco_unitario" />
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Data</mat-label>
        <input matInput type="date" formControlName="data_operacao" />
      </mat-form-field>

      <button mat-raised-button color="primary" type="submit" [disabled]="loading">
        {{ loading ? 'Calculando...' : 'Calcular' }}
      </button>

      <button mat-stroked-button type="button" (click)="resetForm()">
        Limpar
      </button>
    </form>

    <div *ngIf="error" class="error-message">{{ error }}</div>
  </mat-card-content>
</mat-card>
```

### 5. Results Component
**Arquivo**: `src/app/components/results/results.component.ts`

```typescript
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { TaxCalculationResult } from '../../models/trade';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css'],
  standalone: true,
  imports: [CommonModule, MatCardModule],
})
export class ResultsComponent {
  @Input() result: TaxCalculationResult | null = null;

  formatCurrency(value: number): string {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('pt-BR');
  }

  getGainLossClass(): string {
    return (this.result?.ganho_prejuizo_bruto ?? 0) >= 0 ? 'gain' : 'loss';
  }
}
```

**HTML** (`results.component.html`):
```html
<mat-card *ngIf="result" class="results-card">
  <mat-card-header>
    <mat-card-title>{{ result.ativo }} — Resultado</mat-card-title>
  </mat-card-header>

  <mat-card-content>
    <table class="results-table">
      <tr>
        <td>Operação:</td>
        <td>{{ result.tipo_operacao_classificacao }}</td>
      </tr>
      <tr>
        <td>Quantidade:</td>
        <td>{{ result.quantidade }}</td>
      </tr>
      <tr>
        <td>Preço Unitário:</td>
        <td>{{ formatCurrency(result.preco_unitario) }}</td>
      </tr>
      <tr>
        <td>Valor Total:</td>
        <td>{{ formatCurrency(result.valor_financeiro) }}</td>
      </tr>
      <tr [ngClass]="getGainLossClass()">
        <td><strong>Ganho/Prejuízo:</strong></td>
        <td><strong>{{ formatCurrency(result.ganho_prejuizo_bruto) }}</strong></td>
      </tr>
      <tr>
        <td>Alíquota:</td>
        <td>{{ (result.aliquota_aplicada * 100).toFixed(0) }}%</td>
      </tr>
      <tr>
        <td>IR Devido:</td>
        <td>{{ formatCurrency(result.ir_devido) }}</td>
      </tr>
      <tr>
        <td>IRRF Retido:</td>
        <td>{{ formatCurrency(result.irrf_retido) }}</td>
      </tr>
      <tr>
        <td><strong>Valor Líquido:</strong></td>
        <td><strong>{{ formatCurrency(result.valor_liquido) }}</strong></td>
      </tr>
    </table>

    <div class="message" *ngIf="result.mensagem">
      <strong>Resumo:</strong> {{ result.mensagem }}
    </div>
  </mat-card-content>
</mat-card>
```

### 6. Chat Component (Phase 3+)
**Arquivo**: `src/app/components/chat/chat.component.ts`

```typescript
import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { ApiService } from '../../services/api.service';
import { ChatMessage } from '../../models/trade';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule, MatInputModule, MatButtonModule],
})
export class ChatComponent {
  messages = signal<ChatMessage[]>([]);
  inputMessage = signal('');
  loading = signal(false);

  constructor(private apiService: ApiService) {}

  sendMessage(): void {
    const message = this.inputMessage().trim();
    if (!message) return;

    this.messages.update((msgs) => [
      ...msgs,
      { role: 'user', content: message },
    ]);

    this.inputMessage.set('');
    this.loading.set(true);

    this.apiService.sendChat(message).subscribe({
      next: (response) => {
        this.messages.update((msgs) => [
          ...msgs,
          {
            role: 'assistant',
            content: response.response,
            trade_extracted: response.trade_extracted,
            calculation_result: response.calculation_result,
          },
        ]);
        this.loading.set(false);
      },
      error: (error) => {
        this.messages.update((msgs) => [
          ...msgs,
          { role: 'assistant', content: 'Erro ao processar mensagem.' },
        ]);
        this.loading.set(false);
      },
    });
  }

  formatCurrency(value: number): string {
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
  }
}
```

### 7. App Component (Main)
**Arquivo**: `src/app/app.component.ts`

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { TradeInputComponent } from './components/trade-input/trade-input.component';
import { ResultsComponent } from './components/results/results.component';
import { ChatComponent } from './components/chat/chat.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    MatTabsModule,
    MatToolbarModule,
    TradeInputComponent,
    ResultsComponent,
    ChatComponent,
  ],
})
export class AppComponent {
  title = 'Assistente Financeiro Brasileiro';
}
```

**HTML** (`app.component.html`):
```html
<mat-toolbar color="primary">
  <span>{{ title }}</span>
</mat-toolbar>

<div class="container">
  <mat-tab-group>
    <mat-tab label="Chat">
      <app-chat></app-chat>
    </mat-tab>

    <mat-tab label="Formulário">
      <app-trade-input></app-trade-input>
    </mat-tab>

    <mat-tab label="Resumo">
      <!-- TODO: Summary component -->
    </mat-tab>

    <mat-tab label="Histórico">
      <!-- TODO: History component -->
    </mat-tab>
  </mat-tab-group>
</div>
```

### 8. Locale PT-BR Setup

**Arquivo**: `angular.json`
```json
{
  "i18n": {
    "sourceLocale": "pt-BR",
    "locales": {
      "pt-BR": {
        "translation": "src/locale/messages.pt-BR.json"
      }
    }
  }
}
```

Use pipe `date` e `currency` com locale:
```html
<!-- Automático com locale pt-BR -->
{{ trade.data_operacao | date : 'dd/MM/yyyy' }}
{{ result.valor_liquido | currency : 'BRL' : 'symbol' : '1.2-2' : 'pt-BR' }}
```

---

## CSS Styling

**Arquivo**: `src/app/app.component.css`
```css
.container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.form-card {
  margin: 20px;
  padding: 20px;
}

.results-card {
  margin: 20px;
  padding: 20px;
  background-color: #f5f5f5;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table tr {
  border-bottom: 1px solid #ddd;
}

.results-table td {
  padding: 10px;
}

.gain {
  color: green;
  font-weight: bold;
}

.loss {
  color: red;
  font-weight: bold;
}

.error-message {
  color: red;
  margin-top: 10px;
  padding: 10px;
  background-color: #ffe0e0;
  border-radius: 4px;
}
```

---

## Testes

### Unit Test: Format Currency

```typescript
describe('TradeInputComponent', () => {
  it('should format currency in PT-BR', () => {
    const value = 2550.50;
    const formatted = value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    });
    expect(formatted).toBe('R$ 2.550,50');
  });
});
```

### E2E Test: Submit Form

```typescript
describe('Trade Input E2E', () => {
  it('should submit form and display results', () => {
    cy.visit('/');
    cy.get('input[formControlName="ativo"]').type('PETR4');
    cy.get('input[formControlName="quantidade"]').type('100');
    cy.get('input[formControlName="preco_unitario"]').type('25.50');
    cy.get('button[type="submit"]').click();

    cy.get('app-results').should('be.visible');
    cy.contains('R$').should('be.visible');
  });
});
```

---

## Validação (Checklist)

- [ ] Angular 17 setup
- [ ] Models TypeScript criados
- [ ] API Service funcional (POST /trades, POST /chat)
- [ ] TradeInputComponent (formulário) completo
- [ ] ResultsComponent exibe corretamente
- [ ] Locale PT-BR (R$, datas DD/MM/YYYY)
- [ ] Material Design aplicado
- [ ] App roda em localhost:4200
- [ ] Testes unitários + E2E passando

---

## Notas

- **Standalone Components**: Angular 17 preferência (sem módulos)
- **Signals vs RxJS**: Signals mais simples para este projeto
- **Material Design**: Fornece componentes polidos e a11y built-in
- **Locale**: Crítico para UX brasileira (nunca mostrar R$2,550.50)
- **Responsive**: Testar em mobile (Bootstrap grid)
