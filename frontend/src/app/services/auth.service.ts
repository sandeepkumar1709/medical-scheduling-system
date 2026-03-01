import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = 'http://localhost:8000';
  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasValidToken());

  isLoggedIn$ = this.isLoggedInSubject.asObservable();

  constructor(private http: HttpClient) {}

  private hasValidToken(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;
    return !this.isTokenExpired();
  }

  isTokenExpired(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return true;
    
    try {
      // Decode JWT payload (base64)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiry = payload.exp * 1000; // Convert to milliseconds
      
      // Check if expired (with 30 second buffer)
      return Date.now() >= (expiry - 30000);
    } catch {
      return true; // Invalid token format
    }
  }

  login(username: string, password: string): Observable<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/login`, formData).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
        this.isLoggedInSubject.next(true);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    this.isLoggedInSubject.next(false);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}
