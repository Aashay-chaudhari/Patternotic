import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { GetDataService } from 'src/services/get-data.service';
import { TradeService } from 'src/services/trade.service';

export interface StockData {
  ticker: string;
  predictedClose: number;
  lastClosePrice: number;
  percentageDifference: number;
}

@Component({
  selector: 'app-market-close',
  templateUrl: './market-close.component.html',
  styleUrls: ['./market-close.component.scss']
})
export class MarketCloseComponent implements OnInit, AfterViewInit {
  username: string = '';
  market: string = '';
  data: MatTableDataSource<StockData> = new MatTableDataSource<StockData>();
  displayedColumns: string[] = ['ticker', 'predictedClose', 'lastClosePrice', 'percentageDifference', 'takeTrade'];
  stocks: string[] = [];
  us_stocks: string[] = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'NVDA', 'NFLX', 'ADBE', 'ORCL', 'INTC', 'CSCO', 'IBM', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU', 'CRM', 'PYPL'];
  nse_stocks: string[] = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "HDFC.NS", "BHARTIARTL.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS", "M&M.NS", "WIPRO.NS"];
  
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;
  isLoading: boolean = false;

  constructor(private router: Router, private getDataService: GetDataService, private tradeService: TradeService) {
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras?.state as { username: string, market: string };
    if (state) {
      this.username = state.username;
      this.market = state.market;
      if (this.market == 'NSE') {
        this.stocks = this.nse_stocks;
      } else {
        this.stocks = this.us_stocks;
      }
      console.log("Username: ", this.username, " Market: ", this.market);
    }
  }

  ngOnInit(): void {
    this.sendStocks();
  }

  ngAfterViewInit() {
    this.data.paginator = this.paginator;
    this.data.paginator._changePageSize(5); // Set the default page size to 5
    this.data.sort = this.sort;
  }

  sendStocks(): void {
    this.isLoading = true;
    this.getDataService.getstockData(this.stocks, this.market).subscribe(
      (response) => {
        const stockData = response.predicted_close.map((item: any[]) => ({
          ticker: item[0],
          predictedClose: Number(item[1]),
          lastClosePrice: Number(item[2]),
          percentageDifference: ((Number(item[1]) - Number(item[2])) / Number(item[2])) * 100
        }));
        this.data.data = stockData;
        this.isLoading = false;
        console.log('Fetched Data:', this.data);
      },
      (error) => {
        this.isLoading = false;
        console.error('Error fetching data', error);
      }
    );
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.data.filter = filterValue.trim().toLowerCase();

    if (this.data.paginator) {
      this.data.paginator.firstPage();
    }
  }

  getRowColor(percentageDifference: number): string {
    if (percentageDifference >= 10) {
      return 'darkgreen';
    } else if (percentageDifference >= 5) {
      return 'green';
    } else if (percentageDifference >= 1) {
      return 'lightgreen';
    } else if (percentageDifference >= 0) {
      return 'yellow';
    } else if (percentageDifference <= -10) {
      return 'darkred';
    } else if (percentageDifference <= -5) {
      return 'red';
    } else if (percentageDifference <= -1) {
      return 'lightcoral';
    } else {
      return 'yellow';
    }
  }

  takeTrade(element: StockData) {
    const positionType = element.predictedClose > element.lastClosePrice ? 'Long' : 'Short';
    const trade = {
      ticker: element.ticker,
      predictedClose: element.predictedClose,
      lastClosePrice: element.lastClosePrice,
      positionType: positionType
    };
    this.tradeService.sendTrade(trade, this.market).subscribe(
      response => {
        console.log('Trade sent successfully', response);
      },
      error => {
        console.error('Error sending trade', error);
      }
    );
  }
}
