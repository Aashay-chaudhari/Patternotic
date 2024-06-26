import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { TradeService } from 'src/services/trade.service';
import { Router } from '@angular/router';

export interface TradeData {
  ticker: string;
  predictedClose: number;
  lastClosePrice: number;
  positionType: string;
  entryPrice: number;
  closePrice: number;
  profit: number;
  date: string;
}

@Component({
  selector: 'app-trade-list',
  templateUrl: './trade-list.component.html',
  styleUrls: ['./trade-list.component.scss']
})
export class TradeListComponent implements OnInit, AfterViewInit {
  data: MatTableDataSource<TradeData> = new MatTableDataSource<TradeData>();
  displayedColumns: string[] = ['date', 'ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit'];

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;
  market: string | null;
  currentSelection: string = '';
  selectedButton: string = '';
  selectedModel: string = 'model1'; // Default to model1

  constructor(private tradeService: TradeService, private router: Router) {
    this.market = localStorage.getItem("market") || 'NSE'; // default to 'nse'
  }

  ngOnInit(): void {
    this.get_trades('user', 'daily', 'User Daily Trades', this.selectedModel);
  }

  ngAfterViewInit() {
    this.data.paginator = this.paginator;
    this.data.sort = this.sort;
  }

  get_trades(user: string, freq: string, selection: string, model: string): void {
    this.currentSelection = selection;
    this.selectedButton = `${user}-${freq}`;

    if (this.market) {
      console.log("Calling get trades with : ", this.market, user, freq, model);
      this.tradeService.getTrades(this.market, user, freq, model).subscribe(
        (response) => {
          const trades: TradeData[] = response.map((item: any) => ({
            ticker: item.ticker,
            predictedClose: this.validateNumber(item.predictedClose),
            lastClosePrice: this.validateNumber(item.lastClosePrice),
            positionType: item.positionType,
            entryPrice: this.validateNumber(item.entryPrice),
            closePrice: this.validateNumber(item.closePrice),
            profit: this.validateNumber(item.profit),
            date: item.date
          }));
          this.data = new MatTableDataSource(trades);
          this.data.paginator = this.paginator;
          this.data.sort = this.sort;
        },
        (error) => {
          console.error('Error fetching trades', error);
        }
      );
    } else {
      console.error('Market value is null');
    }
  }

  validateNumber(value: any): number {
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.data.filter = filterValue.trim().toLowerCase();

    if (this.data.paginator) {
      this.data.paginator.firstPage();
    }
  }

  toggleMarket(): void {
    this.market = this.market === 'NSE' ? 'NASDAQ' : 'NSE';
    localStorage.setItem("market", this.market);
    this.get_trades('user', 'daily', 'User Daily Trades', this.selectedModel);
  }

  selectModel(model: string): void {
    this.selectedModel = model;
    this.get_trades('user', 'daily', 'User Daily Trades', this.selectedModel);
  }

  logout(): void {
    localStorage.removeItem("user");
    localStorage.removeItem("market");
    this.router.navigate(['/']);
  }
}
