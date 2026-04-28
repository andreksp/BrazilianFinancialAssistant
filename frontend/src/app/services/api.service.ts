/**
 * API Service for communicating with FastAPI backend.
 *
 * Endpoints:
 * - POST /api/trades/process - Process a trade
 * - POST /api/chat/message - Send chat message
 * - GET /api/calculations/summary - Get monthly summary
 */

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

  /**
   * Process a single trade.
   *
   * Calculates taxes, fees, and net value.
   */
  processTrade(trade: TradeInput): Observable<TaxCalculationResult> {
    return this.http.post<TaxCalculationResult>(
      `${this.apiUrl}/trades/process`,
      trade
    );
  }

  /**
   * Send a chat message.
   *
   * Natural language trade input with LLM parsing.
   */
  sendChat(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(
      `${this.apiUrl}/chat/message`,
      request
    );
  }

  /**
   * Get monthly tax summary.
   *
   * Used for DARF calculation and tax declaration.
   */
  getMonthlySummary(month: number, year: number): Observable<MonthlyTaxSummary> {
    const params = new HttpParams()
      .set('month', month.toString())
      .set('year', year.toString());

    return this.http.get<MonthlyTaxSummary>(
      `${this.apiUrl}/calculations/summary`,
      { params }
    );
  }

  /**
   * Get calculation by ID.
   */
  getCalculation(calculationId: string): Observable<TaxCalculationResult> {
    return this.http.get<TaxCalculationResult>(
      `${this.apiUrl}/calculations/${calculationId}`
    );
  }

  /**
   * Get DARF information for a month.
   */
  getDarfInfo(month: number, year: number): Observable<any> {
    const params = new HttpParams()
      .set('month', month.toString())
      .set('year', year.toString());

    return this.http.get<any>(
      `${this.apiUrl}/calculations/darf`,
      { params }
    );
  }

  /**
   * Test hello endpoint - infrastructure verification.
   */
  hello(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/hello`);
  }
}
