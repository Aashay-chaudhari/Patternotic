import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  username: string = '';
  market: string = '';
  marketStatus: string = '';

  constructor(private router: Router, private cdr: ChangeDetectorRef) {
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras?.state as { username: string, market: string };
    if (state) {
      this.username = state.username;
      this.market = state.market;
      console.log("Username: ", this.username, " Market: ", this.market);
    }
  }

  ngOnInit(): void {
    console.log("Inside ngOnInit");
    this.checkMarketStatus();
  }

  checkMarketStatus() {
    console.log("Inside check market status for ", this.username, this.market);

    const currentTime = new Date();
    const day = currentTime.getDay();

    if (this.market === 'NSE') {
      // Convert to IST
      const istTime = new Date(currentTime.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
      const istDay = istTime.getDay();
      const istHours = istTime.getHours();
      const istMinutes = istTime.getMinutes();

      // NSE market open hours: Monday to Friday, 9:15 AM to 3:30 PM (IST)
      if (istDay >= 1 && istDay <= 5 &&
          (istHours > 9 || (istHours === 9 && istMinutes >= 15)) &&
          (istHours < 15 || (istHours === 15 && istMinutes <= 30))) {
        console.log("Routing to market open")
        this.router.navigate(['/market-open'], { state: { username: this.username, market: this.market } });
        this.marketStatus = 'Market Open';
      } else {
        console.log("Routing to market closed")

        this.router.navigate(['/market-close'], { state: { username: this.username, market: this.market } });
        this.marketStatus = 'Market Closed';
      }
      console.log("Market status for NSE: ", this.marketStatus);

    } else if (this.market === 'NASDAQ') {
      // Convert to EST
      const estTime = new Date(currentTime.toLocaleString('en-US', { timeZone: 'America/New_York' }));
      const estDay = estTime.getDay();
      const estHours = estTime.getHours();
      const estMinutes = estTime.getMinutes();

      // NASDAQ market open hours: Monday to Friday, 9:30 AM to 4:00 PM (EST)
      if (estDay >= 1 && estDay <= 5 &&
          (estHours > 9 || (estHours === 9 && estMinutes >= 30)) &&
          estHours < 16) {
        this.router.navigate(['/market-open'], { state: { username: this.username, market: this.market } });
        this.marketStatus = 'Market Open';
      } else {
        this.router.navigate(['/market-close'], { state: { username: this.username, market: this.market } });
        this.marketStatus = 'Market Closed';
      }
      console.log("Market status for NASDAQ: ", this.marketStatus);
    }

    // Manually trigger change detection to ensure the view updates
    this.cdr.detectChanges();
  }
}
