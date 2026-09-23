import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';
import { forkJoin, of, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-historico',
  templateUrl: './historico.component.html',
  styleUrls: ['./historico.component.css'],
})
export class HistoricoComponent {
  mes: number = new Date().getMonth() + 1;
  ano: number = new Date().getFullYear();
  loading = false;
  loaded = false;
  summary: any = null;
  darf: any = null;
  trades: any[] = [];
  error: string | null = null;

  meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
  ];

  anos = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - i);

  constructor(private api: ApiService) {}

  load(): void {
    this.loading = true;
    this.loaded = false;
    this.error = null;
    this.summary = null;
    this.darf = null;
    this.trades = [];

    forkJoin({
      summary: this.api.getMonthlySummary(this.mes, this.ano).pipe(
        catchError(e => e.status === 404 ? of(null) : throwError(() => e))
      ),
      darf: this.api.getDarfInfo(this.mes, this.ano),
      trades: this.api.getTradeHistory(this.mes, this.ano),
    }).subscribe({
      next: ({ summary, darf, trades }) => {
        this.summary = summary;
        this.darf = summary ? darf : null;
        this.trades = trades;
        this.loading = false;
        this.loaded = true;
      },
      error: () => {
        this.error = 'Erro ao carregar o período. Tente novamente.';
        this.loading = false;
      },
    });
  }

  formatCurrency(value: number): string {
    return value?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) ?? 'R$ 0,00';
  }

  formatDate(raw: string): string {
    if (!raw) return '—';
    const [y, m, d] = raw.split('-');
    return `${d}/${m}/${y}`;
  }

  irAPagar(): number {
    if (!this.summary) return 0;
    return Math.max(0, (this.summary.ir_total_devido || 0) - (this.summary.irrf_retido_total || 0));
  }
}
