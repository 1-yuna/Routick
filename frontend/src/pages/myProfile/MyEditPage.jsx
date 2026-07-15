// pages/myProfile/MyEditPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import PersonIcon from '../../assets/icons/person.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useUserStore from '../../store/userStore.jsx';
import { updateMe } from '../../api/user.jsx';
import { getImageUrl } from '../../utils/imageUtil.jsx';

// 프로필 변경 페이지
export default function MyEditPage() {
  const { user, updateUser } = useUserStore();
  const navigate = useNavigate();
  const [nickname, setNickname] = useState(user.nickname ?? '');
  const [imageFile, setImageFile] = useState(null); // 서버로 보낼 실제 파일
  const [preview, setPreview] = useState(getImageUrl(user.profileImageUrl)); // 미리보기
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    if (!nickname || nickname.length < 2 || nickname.length > 10) {
      setError('닉네임은 2~10자로 입력해주세요');
      return;
    }
    try {
      setSaving(true);
      const res = await updateMe(nickname, imageFile);
      updateUser(res.data.data);
      navigate(-1);
    } catch (e) {
      setError(e.response?.data?.message ?? '수정에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-white">
      <TopBar className="px-6" title="프로필 변경" onClick={() => navigate(-1)}>
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="flex flex-col items-center px-6 py-8 gap-6 flex-1">
        <div className="flex flex-col items-center gap-3">
          <div className="w-24 h-24 rounded-full bg-line1 flex items-center justify-center overflow-hidden">
            {preview ? (
              <img
                src={preview}
                alt="프로필"
                className="w-full h-full object-cover"
              />
            ) : (
              <PersonIcon className="w-12 h-12 text-white" />
            )}
          </div>
          <button
            className="px-6 py-2 border border-line1 text-14-rg text-black1"
            onClick={() => document.getElementById('profile-image').click()}
          >
            사진 변경
          </button>
          <input
            id="profile-image"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleImageChange}
          />
        </div>

        <div className="flex flex-col gap-2 w-full">
          <p className="text-14-rg text-black1">닉네임</p>
          <input
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="닉네임을 입력하세요"
            className="w-full bg-neutral rounded-5 px-3 py-2 text-14-rg text-black1 outline-none"
          />
          {error && <p className="text-12-rg text-red">{error}</p>}
        </div>
      </div>

      <div className="px-6 pb-6">
        <FullWidthButton
          text={saving ? '저장 중...' : '저장하기'}
          className="bg-primary"
          onClick={handleSave}
        />
      </div>

      <BottomBar />
    </div>
  );
}
