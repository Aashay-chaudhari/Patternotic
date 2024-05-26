// src/app/services/trade.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TradeService {

  baseURL = environment['baseURL']
  private tradeUrl = this.baseURL + '/api/trade';  // Adjust the URL to your backend endpoint
  private getTradesUrl = this.baseURL + '/api/getTrades';  // New endpoint to fetch trades

  constructor(private http: HttpClient) {}

  sendTrade(trade: any, market: any, model : any): Observable<any> {
    const payload = { trade , market, model};
    return this.http.post(this.tradeUrl, payload);
  }

  getTrades(market : any, user : any ,freq: any, model : any): Observable<any> {
    const payload = { market, user,  freq, model};
    // return this.http.post(this.getTradesUrl, {market});
    return this.http.post(this.getTradesUrl, payload);

  }
}
