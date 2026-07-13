// 상대 이미지 경로(/images/xxx)에 서버 호스트를 붙여 절대경로로 변환
const IMAGE_HOST = import.meta.env.VITE_API_BASE_URL.replace(
  /\/api\/v1\/?$/,
  ''
);

export const getImageUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path; // 이미 절대경로면 그대로
  return `${IMAGE_HOST}${path}`;
};
