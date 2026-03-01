import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  Party, 
  PartyAvailability, 
  CarePathItem, 
  OptimalSlotResponse, 
  BookingRequest, 
  Appointment 
} from './api.models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  // Parties
  getParties(): Observable<Party[]> {
    return this.http.get<Party[]>(`${this.baseUrl}/parties`);
  }

  // Availability
  getAvailability(day: number): Observable<PartyAvailability[]> {
    return this.http.get<PartyAvailability[]>(`${this.baseUrl}/availability/${day}`);
  }

    updateAvailability(partyId: number, day: number, slots: number[]): Observable<any> {
    return this.http.put(`${this.baseUrl}/availability`, {
      party_id: partyId,
      day_of_week: day,
      slots: slots
    });
  }


  // Scheduling
   findOptimalSlot(day: number, carePath: CarePathItem[]): Observable<OptimalSlotResponse> {
    return this.http.post<OptimalSlotResponse>(`${this.baseUrl}/find-optimal-slot`, {
      day_of_week: day,
      care_path: carePath
    });
  }


  // Appointments
  createAppointment(booking: BookingRequest): Observable<Appointment> {
    return this.http.post<Appointment>(`${this.baseUrl}/appointments`, booking);
  }

  getAppointments(day?: number): Observable<Appointment[]> {
    const url = day !== undefined 
      ? `${this.baseUrl}/appointments?day=${day}`
      : `${this.baseUrl}/appointments`;
    return this.http.get<Appointment[]>(url);
  }
}
