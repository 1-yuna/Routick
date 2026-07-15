import { denormalizeCourse } from './courseUtils.jsx';

export const buildTripCreatePayload = (course, title) => {
  const { days } = denormalizeCourse(course);
  const payload = {
    preferenceId: course.preferenceId,
    title: title?.trim() || '나의 여행',
    transport: course.transport,
    days,
  };
  if (course.region) {
    payload.region = course.region;
  } else {
    payload.startRegion = course.startRegion;
    payload.endRegion = course.endRegion;
  }
  return payload;
};

export const buildTripDaysUpdatePayload = (course) => {
  const { days } = denormalizeCourse(course);
  return { days };
};
