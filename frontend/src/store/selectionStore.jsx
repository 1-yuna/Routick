// src/store/selectionStore.jsx
import { create } from 'zustand';

const useSelectionStore = create((set) => ({
  address: { name: '', x: '', y: '' },
  period: '',
  companion: '',
  age: '',
  mood: [],
  // ... 나머지 7개

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

  reset: () =>
    set({
      address: { name: '', x: '', y: '' },
      period: '',
      companion: '',
      age: '',
      mood: [],
    }),
}));

export default useSelectionStore;
