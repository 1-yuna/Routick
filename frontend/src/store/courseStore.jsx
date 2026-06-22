import { create } from 'zustand';
import { mockCourse } from '../data/mock/courses.jsx';

const useCourseStore = create((set) => ({
  course: mockCourse,
  setCourse: (course) => set({ course }),
  reset: () => set({ course: mockCourse }),
}));

export default useCourseStore;
