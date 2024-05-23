import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { TradeService } from 'src/services/trade.service';

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

  constructor(private tradeService: TradeService) {
    this.market = localStorage.getItem("market");
  }

  ngOnInit(): void {
    if (this.market) {
      this.fetchTrades();
    } else {
      console.error('Market value is null');
    }
  }

  ngAfterViewInit() {
    this.data.paginator = this.paginator;
    this.data.sort = this.sort;
  }

  fetchTrades(): void {
    if (this.market) {
      this.tradeService.getTrades(this.market).subscribe(
        (response) => {
          const trades: TradeData[] = response.map((item: any) => ({
            ticker: item.ticker,
            predictedClose: item.predictedClose,
            lastClosePrice: item.lastClosePrice,
            positionType: item.positionType,
            entryPrice: item.entryPrice,
            closePrice: item.closePrice,
            profit: item.profit,
            date: item.date
          }));
          this.data.data = trades;
        },
        (error) => {
          console.error('Error fetching trades', error);
        }
      );
    } else {
      console.error('Market value is null');
    }
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.data.filter = filterValue.trim().toLowerCase();

    if (this.data.paginator) {
      this.data.paginator.firstPage();
    }
  }
}
