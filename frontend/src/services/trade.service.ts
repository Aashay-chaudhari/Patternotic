// src/app/services/trade.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TradeService {
  private tradeUrl = 'http://3.21.231.62/api/trade';  // Adjust the URL to your backend endpoint
  private getTradesUrl = 'http://3.21.231.62/getTrades';  // New endpoint to fetch trades
  private getBotTradesUrl = 'http://3.21.231.62/getBotTrades';  // New endpoint to fetch trades

  constructor(private http: HttpClient) {}

  sendTrade(trade: any, market: any): Observable<any> {
    const payload = { trade , market};
    return this.http.post(this.tradeUrl, payload);
  }

  getTrades(market : any, user : any ,freq: any): Observable<any> {
    const payload = { market, user,  freq};
    // return this.http.post(this.getTradesUrl, {market});
    return this.http.post(this.getTradesUrl, payload);

  }
  
  getBotTrades(market : any): Observable<any> {
    return this.http.post(this.getBotTradesUrl, {market});
  }
}
