import { useNavigate } from 'react-router-dom';

import fail from '../../assets/images/fail.png';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';

export default function FailPage() {
  const navigate = useNavigate();

  return (
    <div className="h-screen bg-white flex flex-col items-center justify-between px-6 pt-12 pb-[88px]">
      {/*캐릭터 + 메시지*/}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        <div className="w-52 h-52 rounded-full overflow-hidden bg-login">
          <img
            src={fail}
            alt="실패 캐릭터"
            className="w-full h-full object-cover scale-110"
          />
        </div>
        <div className="flex flex-col items-center gap-1">
          <p className="text-16-sb text-black1">일정 생성에 실패했어요</p>
          <p className="text-14-rg text-gray2">
            일시적인 오류로 일정을 만들지 못했어요
          </p>
        </div>
      </div>

      {/*버튼 영역*/}
      <div className="w-full flex flex-col items-center gap-4">
        <button
          onClick={() => navigate('/home')}
          className="text-12-rg text-gray2"
        >
          홈으로 가기
        </button>
        <FullWidthButton
          text="다시 시도하기"
          className="bg-primary"
          onClick={() => navigate('/loading')}
        />
      </div>
    </div>
  );
}
