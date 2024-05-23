import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private router: Router) {}

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    
    // Here you should implement your logic to check if the user is authenticated
    const isAuthenticated = this.checkLogin();

    if (!isAuthenticated) {
      // Redirect to login page if not authenticated
      this.router.navigate(['/login']);
    }
    return isAuthenticated;
  }

  checkLogin(): boolean {
    // Replace this with real authentication check
    // For example, check if a token exists in localStorage
    return !!localStorage.getItem('user');
  }
}
