import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { SchedulingComponent } from './pages/scheduling/scheduling.component';

export const routes: Routes = [
  { path: '', component: SchedulingComponent },
  { path: 'login', component: LoginComponent }
];
