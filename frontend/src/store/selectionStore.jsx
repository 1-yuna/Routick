// src/store/selectionStore.jsx
import { create } from 'zustand';

const useSelectionStore = create((set) => ({
  address: { name: '', lat: '', lng: '', placeId: '' },
  period: '',
  companion: '',
  age: '',
  mood: [],
  activity: [],
  transport: '',
  dislike: [],

  setAddress: (data) => set({ address: data }),
  setPeriod: (data) => set({ period: data }),
  setCompanion: (data) => set({ companion: data }),
  setAge: (data) => set({ age: data }),
  setMood: (value) =>
    set((state) => ({
      mood: state.mood.includes(value)
        ? state.mood.filter((v) => v !== value)
        : [...state.mood, value],
    })),
  setActivity: (value) =>
    set((state) => ({
      activity: state.activity.includes(value)
        ? state.activity.filter((v) => v !== value)
        : [...state.activity, value],
    })),
  setTransport: (data) => set({ transport: data }),
  setDislike: (data) => set({ dislike: data }),

  reset: () =>
    set({
      address: { name: '', lat: '', lng: '', placeId: '' },
      period: '',
      companion: '',
      age: '',
      mood: [],
      activity: [],
      transport: '',
      dislike: [],
    }),
}));

export default useSelectionStore;
