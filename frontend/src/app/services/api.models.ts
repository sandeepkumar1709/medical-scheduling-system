export interface Party {
  id: number;
  name: string;
  color: string;
}

export interface PartyAvailability {
  party_id: number;
  party_name: string;
  party_color: string;
  availability_slots: number[];
  booking_slots: number[];
  patient_names: string[];
  patient_ids?: number[];
}



export interface CarePathItem {
  party_id: number;
  duration_slots: number;
}


export interface OptimalSlotResponse {
  found: boolean;
  start_slot: number | null;
  end_slot: number | null;
  message?: string;
  schedule?: ScheduleItem[];
}


export interface ScheduleItem {
  party_id: number;
  start_slot: number;
  end_slot: number;
}

export interface BookingRequest {
  patient_name: string;
  day_of_week: number;
  start_slot: number;
  end_slot: number;
  care_path: CarePathItem[];
  schedule: ScheduleItem[];
  notes?: string;
  created_by?: string;
}


export interface Appointment {
  id: number;
  patient_name: string;
  patient_id?: number;
  day_of_week: number;
  start_slot: number;
  end_slot: number;
  care_path: CarePathItem[];
  status: string;
  notes: string | null;
  created_by?: string;
  created_at: string;
}
