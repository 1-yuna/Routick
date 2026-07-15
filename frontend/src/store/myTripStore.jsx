import { create } from 'zustand';

const useMyTripStore = create((set) => ({
  trips: [],
  setTrips: (trips) => set({ trips }),

  addTrip: (trip) => set((state) => ({ trips: [trip, ...state.trips] })),
  deleteTrips: (ids) =>
    set((state) => ({
      trips: state.trips.filter((t) => !ids.includes(t.tripId)),
    })),
  updateTripImage: (id, imageUrl) =>
    set((state) => ({
      trips: state.trips.map((t) =>
        t.tripId === id ? { ...t, coverImageUrl: imageUrl } : t
      ),
    })),
  updateTripTitle: (id, title) =>
    set((state) => ({
      trips: state.trips.map((t) => (t.tripId === id ? { ...t, title } : t)),
    })),
}));

export default useMyTripStore;
