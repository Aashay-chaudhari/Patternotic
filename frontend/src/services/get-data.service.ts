import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
@Injectable({
  providedIn: 'root'
})
export class GetDataService {

  base_url = environment['baseURL']
  private apiUrl = this.base_url + '/api/data'; // Flask API URL

  constructor(private http: HttpClient) { }

  getstockData(stocks: string[], market : string, model : string): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const payload = { stocks , market, model};
    return this.http.post<any>(this.apiUrl, payload, { headers });
  }
}