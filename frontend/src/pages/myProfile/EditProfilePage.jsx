// pages/my/ProfilePage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import BottomBar from '../../common/bar/BottomBar.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import FullWidthInput from '../../common/input/FullWidthInput.jsx';
import PersonIcon from '../../assets/icons/person.svg?react';
import LeftIcon from '../../assets/icons/left.svg?react';
import useUserStore from '../../store/userStore.jsx';

// 프로필 변경 페이지
export default function EditProfilePage() {
  const navigate = useNavigate();
  const { user, updateUser } = useUserStore();
  const [name, setName] = useState(user.name);
  const [src, setSrc] = useState(user.src);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSrc(URL.createObjectURL(file));
  };

  const handleSave = () => {
    updateUser({ name, src });
    navigate(-1);
  };

  return (
    <div className="pt-12 pb-32 flex flex-col h-screen bg-white">
      {/*상단 바*/}
      <TopBar
        className="px-6 border-b border-line1"
        title="프로필 변경"
        onClick={() => navigate(-1)}
      >
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="flex flex-col items-center px-6 py-8 gap-6 flex-1">
        {/*프로필 이미지*/}
        <div className="flex flex-col items-center gap-3">
          <div className="w-24 h-24 rounded-full bg-line1 flex items-center justify-center overflow-hidden">
            {src ? (
              <img
                src={src}
                alt="프로필"
                className="w-full h-full object-cover"
              />
            ) : (
              <PersonIcon className="w-12 h-12 text-white" />
            )}
          </div>
          <button
            className="px-4 py-2 border border-line2 rounded-[5px] text-14-rg text-gray2"
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

        {/*닉네임*/}
        <div className="flex flex-col gap-2 w-full">
          <p className="text-14-rg text-black1">닉네임</p>
          <FullWidthInput
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="닉네임 입력"
          />
        </div>
      </div>

      {/*저장 버튼*/}
      <div className="px-6 pb-6">
        <FullWidthButton
          text="저장하기"
          className="bg-primary"
          onClick={handleSave}
        />
      </div>

      <BottomBar />
    </div>
  );
}
