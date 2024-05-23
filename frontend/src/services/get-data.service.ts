import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GetDataService {

  private apiUrl = 'http://localhost:5000/data'; // Flask API URL

  constructor(private http: HttpClient) { }

  getstockData(stocks: string[], market : string): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const payload = { stocks , market};
    return this.http.post<any>(this.apiUrl, payload, { headers });
  }
}