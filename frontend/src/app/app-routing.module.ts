import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './auth.guard';
import { MarketOpenComponent } from './market-open/market-open.component';
import { MarketCloseComponent } from './market-close/market-close.component';
import { TradeListComponent } from './trade-list/trade-list.component';
import { BotTradeListComponent } from './bot-trade-list/bot-trade-list.component';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent , canActivate: [AuthGuard] },
  { path: 'market-open', component: MarketOpenComponent , canActivate: [AuthGuard] },
  { path: 'market-close', component: MarketCloseComponent , canActivate: [AuthGuard] },
  { path: 'trade-list', component: TradeListComponent ,canActivate: [AuthGuard]},
  { path: 'bot-trade-list', component: BotTradeListComponent ,canActivate: [AuthGuard]}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
