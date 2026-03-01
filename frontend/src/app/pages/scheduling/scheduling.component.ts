import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { PartyAvailability, CarePathItem, OptimalSlotResponse } from '../../services/api.models';

@Component({
  selector: 'app-scheduling',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './scheduling.component.html',
  styleUrls: ['./scheduling.component.scss']
})

export class SchedulingComponent implements OnInit {
  // Data from API
  availability: PartyAvailability[] = [];
  
  // Day selection (0=Monday, 6=Sunday)
  selectedDay = 0;
  days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
  // Time slots (36 slots: 8AM-5PM, 15min each)
  timeSlots: string[] = [];

  // Auth status
  isLoggedIn = false;

    // Care path builder
  carePath: CarePathItem[] = [];
  selectedPartyId = 1;
  selectedSlots = 1;

    // Booking
  patientName = '';
  optimalSlot: OptimalSlotResponse | null = null;

  isSearching = false;
  isBooking = false;
  bookingMessage = '';

    // Edit mode for blocking slots
  isEditMode = false;

  // Selection for blocking
  selectedCells: { partyId: number; slotIndex: number }[] = [];
  isDragging = false;
  
  // Loading states
  isLoadingAvailability = false;
  isSavingBlock = false;


  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) {
    this.generateTimeSlots();
  }

    generateTimeSlots(): void {
    // Generate 36 time slots from 8:00 AM to 5:00 PM (15 min intervals)
    for (let hour = 8; hour < 17; hour++) {
      for (let min = 0; min < 60; min += 15) {
        const time = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
        this.timeSlots.push(time);
      }
    }
  }

    loadAvailability(): void {
    this.isLoadingAvailability = true;
    this.apiService.getAvailability(this.selectedDay).subscribe({
      next: (data) => {
        this.availability = data;
        this.isLoadingAvailability = false;
        this.clearSelection();
      },
      error: (err) => {
        console.error('Failed to load availability', err);
        this.isLoadingAvailability = false;
      }
    });
  }


    getSlotTooltip(party: PartyAvailability, slotIndex: number): string {
    // Returns tooltip text when hovering over a slot
    if (party.booking_slots[slotIndex] === 1) {
      const patientName = party.patient_names[slotIndex];
      return patientName ? `Booked for patient ${patientName}` : 'Booked';
    }
    if (party.availability_slots[slotIndex] === 1) {
      return 'Blocked';
    }
    return 'Available';
  }

  formatSlotTime(slotIndex: number): string {
    // Converts slot index (0-35) to time string ("08:00", etc.)
    return this.timeSlots[slotIndex] || '';
  }


   onDayChange(): void {
    // Called when user selects a different day from dropdown
    this.loadAvailability();
  }

    getSlotClass(party: PartyAvailability, slotIndex: number): string {
    let classes = '';
    if (party.booking_slots[slotIndex] === 1) {
      classes = 'booked';
    } else if (party.availability_slots[slotIndex] === 1) {
      classes = 'blocked';
    } else {
      classes = 'free';
    }
    
    // Add selected class if this cell is selected
    if (this.isCellSelected(party.party_id, slotIndex)) {
      classes += ' selected';
    }
    
    // Highlight optimal slot
    if (this.isOptimalSlot(party.party_id, slotIndex)) {
      classes += ' optimal';
    }
    
    return classes;
  }

  isOptimalSlot(partyId: number, slotIndex: number): boolean {
    if (!this.optimalSlot?.found || !this.optimalSlot.schedule) {
      return false;
    }
    
    return this.optimalSlot.schedule.some(item => 
      item.party_id === partyId && 
      slotIndex >= item.start_slot && 
      slotIndex <= item.end_slot
    );
  }




  ngOnInit(): void {
    // We'll add initialization here
    this.authService.isLoggedIn$.subscribe(loggedIn => {
      this.isLoggedIn = loggedIn;
    });
    
    // Load availability for default day (Monday)
    this.loadAvailability();
  }

    // Care path methods
  addToCarePath(): void {
  // Prevent Gap as first item
  if (this.carePath.length === 0 && Number(this.selectedPartyId) === 0) {
    this.bookingMessage = 'Cannot start care path with a gap';
    return;
  }
  this.bookingMessage = ''; 
  
  this.carePath.push({
    party_id: Number(this.selectedPartyId),
    duration_slots: Number(this.selectedSlots)
  });
}




  removeFromCarePath(index: number): void {
    // Remove a step from the care path
    this.carePath.splice(index, 1);
  }

  getPartyName(partyId: number): string {
    if (partyId === 0) return 'Gap (Wait Time)';
    const party = this.availability.find(p => p.party_id === partyId);
    return party ? party.party_name : 'Unknown';
  }


    getTotalSlots(): number {
    return this.carePath.reduce((sum, item) => sum + item.duration_slots, 0);
  }


    // Scheduling & Booking methods
  findOptimal(): void {
    if (this.carePath.length === 0) {
      this.bookingMessage = 'Please add at least one step to the care path';
      return;
    }

    this.isSearching = true;
    this.optimalSlot = null;
    this.bookingMessage = '';

    // Call the NumPy algorithm on the backend
    this.apiService.findOptimalSlot(this.selectedDay, this.carePath).subscribe({
      next: (result) => {
        this.optimalSlot = result;
        this.isSearching = false;
      },
      error: (err) => {
        this.bookingMessage = 'Error finding optimal slot';
        this.isSearching = false;
      }
    });
  }

  bookAppointment(): void {
    if (!this.patientName.trim()) {
      this.bookingMessage = 'Please enter patient name';
      return;
    }
    if (!this.optimalSlot?.found || this.optimalSlot.start_slot === null) {
      this.bookingMessage = 'Please find an optimal slot first';
      return;
    }

    this.isBooking = true;
    this.bookingMessage = '';

    this.apiService.createAppointment({
      patient_name: this.patientName,
      day_of_week: this.selectedDay,
      start_slot: this.optimalSlot.start_slot!,
      end_slot: this.optimalSlot.end_slot!,
      care_path: this.carePath,
      schedule: this.optimalSlot.schedule!
    }).subscribe({

      next: () => {
        this.bookingMessage = 'Appointment booked successfully!';
        this.isBooking = false;
        // Reset form
        this.patientName = '';
        this.carePath = [];
        this.optimalSlot = null;
        // Reload grid to show new booking
        this.loadAvailability();
      },
      error: (err) => {
        this.bookingMessage = err.status === 401 
          ? 'Please login to book appointments' 
          : 'Error booking appointment';
        this.isBooking = false;
      }
    });
  }

    // Selection methods
  isCellSelected(partyId: number, slotIndex: number): boolean {
    return this.selectedCells.some(c => c.partyId === partyId && c.slotIndex === slotIndex);
  }

  onCellMouseDown(party: PartyAvailability, slotIndex: number, event: MouseEvent): void {
    if (!this.isLoggedIn) return;
    if (party.booking_slots[slotIndex] === 1) return; // Can't select booked slots
    
    event.preventDefault();
    this.isDragging = true;
    this.toggleCellSelection(party.party_id, slotIndex);
  }

  onCellMouseEnter(party: PartyAvailability, slotIndex: number): void {
    if (!this.isDragging || !this.isLoggedIn) return;
    if (party.booking_slots[slotIndex] === 1) return;
    
    // Add to selection if not already selected
    if (!this.isCellSelected(party.party_id, slotIndex)) {
      this.selectedCells.push({ partyId: party.party_id, slotIndex });
    }
  }

  onCellMouseUp(): void {
    this.isDragging = false;
  }

  toggleCellSelection(partyId: number, slotIndex: number): void {
    const index = this.selectedCells.findIndex(
      c => c.partyId === partyId && c.slotIndex === slotIndex
    );
    
    if (index >= 0) {
      this.selectedCells.splice(index, 1);
    } else {
      this.selectedCells.push({ partyId, slotIndex });
    }
  }

  clearSelection(): void {
    this.selectedCells = [];
  }

  blockSelectedSlots(): void {
    if (this.selectedCells.length === 0 || !this.isLoggedIn) return;
    
    this.isSavingBlock = true;
    
    // Group by party
    const byParty = new Map<number, number[]>();
    for (const cell of this.selectedCells) {
      if (!byParty.has(cell.partyId)) {
        byParty.set(cell.partyId, []);
      }
      byParty.get(cell.partyId)!.push(cell.slotIndex);
    }
    
    // Update each party
    let completed = 0;
    const total = byParty.size;
    
    byParty.forEach((slots, partyId) => {
      const party = this.availability.find(p => p.party_id === partyId);
      if (!party) return;
      
      const newSlots = [...party.availability_slots];
      slots.forEach(slotIndex => {
        newSlots[slotIndex] = 1; // Block
      });
      
      this.apiService.updateAvailability(partyId, this.selectedDay, newSlots).subscribe({
        next: () => {
          party.availability_slots = newSlots;
          completed++;
          if (completed === total) {
            this.isSavingBlock = false;
            this.clearSelection();
            this.bookingMessage = 'Slots blocked successfully';
          }
        },
        error: () => {
          this.isSavingBlock = false;
          this.bookingMessage = 'Error blocking slots';
        }
      });
    });
  }

  unblockSelectedSlots(): void {
    if (this.selectedCells.length === 0 || !this.isLoggedIn) return;
    
    this.isSavingBlock = true;
    
    const byParty = new Map<number, number[]>();
    for (const cell of this.selectedCells) {
      if (!byParty.has(cell.partyId)) {
        byParty.set(cell.partyId, []);
      }
      byParty.get(cell.partyId)!.push(cell.slotIndex);
    }
    
    let completed = 0;
    const total = byParty.size;
    
    byParty.forEach((slots, partyId) => {
      const party = this.availability.find(p => p.party_id === partyId);
      if (!party) return;
      
      const newSlots = [...party.availability_slots];
      slots.forEach(slotIndex => {
        newSlots[slotIndex] = 0; // Unblock
      });
      
      this.apiService.updateAvailability(partyId, this.selectedDay, newSlots).subscribe({
        next: () => {
          party.availability_slots = newSlots;
          completed++;
          if (completed === total) {
            this.isSavingBlock = false;
            this.clearSelection();
            this.bookingMessage = 'Slots unblocked successfully';
          }
        },
        error: () => {
          this.isSavingBlock = false;
          this.bookingMessage = 'Error unblocking slots';
        }
      });
    });
  }



    logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }



}
