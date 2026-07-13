import api from './axios';

// 내 정보 조회 (스플래시 로그인 상태 확인 겸용)
export const getMe = () => api.get('/users/me');

// 내 정보 수정 (닉네임/프로필 이미지, multipart)
export const updateMe = (nickname, profileImageFile) => {
  const formData = new FormData();
  if (nickname !== undefined && nickname !== null)
    formData.append('nickname', nickname);
  if (profileImageFile) formData.append('profileImage', profileImageFile);
  return api.patch('/users/me', formData); // Content-Type은 axios가 FormData 보고 자동 세팅 (boundary 포함)
};

// 회원 탈퇴
export const deleteMe = () => api.delete('/users/me');

// 마지막 위치 저장 (홈 지역 드롭다운 선택 시)
export const updateLocation = (regionName, lat, lng) =>
  api.patch('/users/me/location', { regionName, lat, lng });
