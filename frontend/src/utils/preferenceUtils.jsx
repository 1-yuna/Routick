const PERIOD_DAYS = { day: 1, '1n2d': 2, '2n3d': 3, '3n4d': 4 };

const formatDate = (date) => {
  if (!date) return null;
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
};

export const buildPreferencePayload = (selection) => {
  const {
    period,
    date,
    transport,
    route,
    address,
    addresses,
    companion,
    mood,
    activity,
    dislike,
  } = selection;

  const base = {
    routeType: route === 'destination' ? 'only' : 'endpoint',
    travelDays: PERIOD_DAYS[period] ?? 1,
    travelDate: formatDate(date?.start),
    transport,
    companion,
    moods: mood,
    activities: activity,
    avoidActivities: dislike,
  };

  if (base.routeType === 'only') {
    return {
      ...base,
      destination: address.name,
      lat: address.lat,
      lng: address.lng,
    };
  }

  return {
    ...base,
    days: addresses.map((day, i) => ({
      dayNumber: i + 1,
      startLat: day.start.lat,
      startLng: day.start.lng,
      startName: day.start.name,
      startAddress: day.start.address,
      startPlaceId: day.start.placeId,
      midLat: day.mid.lat,
      midLng: day.mid.lng,
      midName: day.mid.name,
      endLat: day.end.lat,
      endLng: day.end.lng,
      endName: day.end.name,
      endAddress: day.end.address,
      endPlaceId: day.end.placeId,
    })),
  };
};
