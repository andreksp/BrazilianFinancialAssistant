import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  activeTab: 'chat' | 'formulario' | 'historico' = 'chat';

  setTab(tab: 'chat' | 'formulario' | 'historico'): void {
    this.activeTab = tab;
  }
}
