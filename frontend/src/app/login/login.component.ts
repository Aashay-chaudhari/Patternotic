import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username: string = '';
  marketSelected: boolean = false;
  market: string = ''

  constructor(private router: Router){}

  selectMarket(market: string) {
    this.marketSelected = true;
    this.market = market;
    console.log('Selected Market:', market);
  }

  onSubmit() {
    // Handle the form submission
    console.log('Username:', this.username);
    console.log('Selected Market:', this.market);
    if (this.username && this.marketSelected) {
      localStorage.setItem("user", this.username)
      localStorage.setItem("market", this.market)
      this.router.navigate(['/home'], { state: { username: this.username, market: this.market } });
    }
  }
}
