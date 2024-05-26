import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { GetDataService } from 'src/services/get-data.service';

export interface StockData {
  ticker: string;
  predictedClose: number;
  lastTradedPrice: number;
  percentageDifference: number; // Add percentage difference property
}

@Component({
  selector: 'app-market-open',
  templateUrl: './market-open.component.html',
  styleUrls: ['./market-open.component.scss']
})
export class MarketOpenComponent implements OnInit, AfterViewInit {
  username: string = '';
  market: string = '';
  data: MatTableDataSource<StockData> = new MatTableDataSource<StockData>();
  displayedColumns: string[] = ['ticker', 'predictedClose', 'lastTradedPrice', 'percentageDifference'];
  stocks: string[] = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'NVDA', 'NFLX', 'ADBE', 'ORCL', 'INTC', 'CSCO', 'IBM', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU', 'CRM', 'PYPL']; // Example list of 20 stocks

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  constructor(private router: Router, private getDataService: GetDataService) {
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras?.state as { username: string, market: string };
    if (state) {
      this.username = state.username;
      this.market = state.market;
      console.log("Username: ", this.username, " Market: ", this.market);
    }
  }

  ngOnInit(): void {
    // this.sendStocks();
  }

  ngAfterViewInit() {
    this.data.paginator = this.paginator;
    this.data.sort = this.sort;
  }

  sendStocks(): void {
    this.getDataService.getstockData(this.stocks, this.market, 'model1').subscribe(
      (response) => {
        const stockData = response.predicted_close.map((item: any[]) => ({
          ticker: item[0],
          predictedClose: Number(item[1][0]), // Ensure the value is a number
          lastTradedPrice: Number(item[2]), // Ensure the value is a number
          percentageDifference: ((Number(item[1][0]) - Number(item[2])) / Number(item[2])) * 100 // Calculate the percentage difference
        }));
        this.data.data = stockData;
        console.log('Fetched Data:', this.data);
      },
      (error) => {
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
    const absDifference = Math.abs(percentageDifference);
    if (absDifference < 1) {
      return 'yellow';
    } else if (percentageDifference > 0) {
      // Increase sensitivity for green color
      const greenIntensity = Math.min(Math.floor((absDifference / 1) * 255), 255);
      return `rgb(0, ${greenIntensity}, 0)`;
    } else {
      // Increase sensitivity for red color
      const redIntensity = Math.min(Math.floor((absDifference / 1) * 255), 255);
      return `rgb(${redIntensity}, 0, 0)`;
    }
  }
}
