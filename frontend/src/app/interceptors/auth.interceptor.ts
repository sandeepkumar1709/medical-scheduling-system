import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.getToken();

  let clonedReq = req;
  
  if (token) {
    // Check if token is expired before making request
    if (authService.isTokenExpired()) {
      authService.logout();
      router.navigate(['/login'], { 
        queryParams: { message: 'Session expired. Please login again.' } 
      });
      return throwError(() => new Error('Token expired'));
    }
    
    clonedReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(clonedReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token rejected by server - logout and redirect
        authService.logout();
        router.navigate(['/login'], { 
          queryParams: { message: 'Session expired. Please login again.' } 
        });
      }
      return throwError(() => error);
    })
  );
};
