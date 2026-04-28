/**
 * Chat Component (Phase 4).
 *
 * Features:
 * - Natural language trade input
 * - Message history display
 * - Trade extraction and calculation display
 * - PT-BR locale formatting
 *
 * TODO: Implement LLM integration in Phase 3
 */

import { Component, OnInit } from '@angular/core';
import { ChatMessage, ChatRequest, ChatResponse } from '../../models/trade';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css'],
})
export class ChatComponent implements OnInit {
  messages: ChatMessage[] = [];
  inputMessage: string = '';
  loading: boolean = false;
  userId: string = 'user123'; // TODO: Get from auth service

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    // Initialize chat
  }

  /**
   * Test backend connectivity with hello endpoint.
   */
  testHello(): void {
    this.loading = true;
    this.apiService.hello().subscribe({
      next: (response) => {
        this.messages.push({
          role: 'assistant',
          content: `✓ Backend conectado: ${response.message}`,
        });
        this.loading = false;
      },
      error: (error) => {
        console.error('Error calling hello:', error);
        this.messages.push({
          role: 'assistant',
          content: '✗ Erro ao conectar ao backend. Verifique se o servidor está rodando.',
        });
        this.loading = false;
      },
    });
  }

  /**
   * Send message to backend.
   *
   * Flow:
   * 1. User types message and presses send
   * 2. API extracts trade (Claude Haiku)
   * 3. Calculate taxes/fees
   * 4. Generate explanation (Claude Sonnet)
   * 5. Display result
   */
  sendMessage(): void {
    if (!this.inputMessage.trim()) {
      return;
    }

    // Add user message to chat
    this.messages.push({
      role: 'user',
      content: this.inputMessage,
    });

    this.loading = true;

    // Send to API
    const request: ChatRequest = {
      message: this.inputMessage,
      user_id: this.userId,
    };

    this.apiService.sendChat(request).subscribe({
      next: (response: ChatResponse) => {
        // Add assistant response
        this.messages.push({
          role: 'assistant',
          content: response.response,
          trade_extracted: response.trade_extracted,
          calculation_result: response.calculation_result,
        });

        this.inputMessage = '';
        this.loading = false;
      },
      error: (error) => {
        console.error('Error sending message:', error);
        this.messages.push({
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao processar sua mensagem.',
        });
        this.loading = false;
      },
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

  /**
   * Format date as DD/MM/YYYY.
   */
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('pt-BR');
  }
}
