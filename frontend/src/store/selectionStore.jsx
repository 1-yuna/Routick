// src/store/selectionStore.jsx
import { create } from 'zustand';

const useSelectionStore = create((set) => ({
  address: { name: '', x: '', y: '' },
  // ... 나머지 7개

  setAddress: (data) => set({ address: data }),

  reset: () => set({ address: { name: '', x: '', y: '' } }),
}));

export default useSelectionStore;
