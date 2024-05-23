// src/app/services/trade.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TradeService {
  private tradeUrl = 'http://localhost:5000/trade';  // Adjust the URL to your backend endpoint
  private getTradesUrl = 'http://localhost:5000/getTrades';  // New endpoint to fetch trades
  private getBotTradesUrl = 'http://localhost:5000/getBotTrades';  // New endpoint to fetch trades

  constructor(private http: HttpClient) {}

  sendTrade(trade: any, market: any): Observable<any> {
    const payload = { trade , market};
    return this.http.post(this.tradeUrl, payload);
  }

  getTrades(market : any): Observable<any> {
    return this.http.post(this.getTradesUrl, {market});
  }
  
  getBotTrades(market : any): Observable<any> {
    return this.http.post(this.getBotTradesUrl, {market});
  }
}
