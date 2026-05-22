// src/store/selectionStore.jsx
import { create } from 'zustand';

const useSelectionStore = create((set) => ({
  address: { name: '', x: '', y: '' },
  period: '',
  // ... 나머지 7개

  setAddress: (data) => set({ address: data }),
  setPeriod: (data) => set({ period: data }),

  reset: () => set({ address: { name: '', x: '', y: '' }, period: '' }),
}));

export default useSelectionStore;
