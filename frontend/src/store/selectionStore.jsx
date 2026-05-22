// src/store/selectionStore.jsx
import { create } from 'zustand';

const useSelectionStore = create((set) => ({
  address: { name: '', x: '', y: '' },
  period: '',
  companion: '',
  // ... 나머지 7개

  setAddress: (data) => set({ address: data }),
  setPeriod: (data) => set({ period: data }),
  setCompanion: (data) => set({ companion: data }),

  reset: () =>
    set({ address: { name: '', x: '', y: '' }, period: '', companion: '' }),
}));

export default useSelectionStore;
