import { useNavigate } from 'react-router-dom';

import TopBar from '../../common/bar/TopBar.jsx';
import PromptText from '../../common/text/PromptText.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';

// 선택 페이지 공통 레이아웃 (8단계 공통 사용)
export default function SelectionLayout({
  step,
  url,
  icon,
  text1,
  text2,
  children,
  onNext,
  disabled,
  subText,
  buttonText,
  contentGap = 'gap-11',
}) {
  const navigate = useNavigate();

  return (
    <div className="pt-12 px-6 h-screen pb-[88px] flex flex-col bg-default">
      {/*상단 바 - url 있으면 해당 경로로, 없으면 이전 페이지로*/}
      <TopBar
        className="text-primary text-16-sb"
        text={`${step}/9`}
        onClick={() => (url ? navigate(url) : navigate(-1))}
      >
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      {/*질문 + 선택 컴포넌트 - 헤더 고정, children만 내부 스크롤*/}
      <div className={`flex flex-col w-full flex-1 min-h-0 ${contentGap}`}>
        <PromptText icon={icon} text1={text1} text2={text2} subText={subText} />
        <div className="flex-1 min-h-0 overflow-y-auto no-scrollbar">
          {children}
        </div>
      </div>

      {/*다음 버튼 - disabled면 비활성화 스타일 및 클릭 막기*/}
      <FullWidthButton
        text={buttonText || '다음'}
        className={
          disabled ? 'bg-primaryOpacity mt-auto' : 'bg-primary mt-auto'
        }
        onClick={disabled ? undefined : onNext}
      />
    </div>
  );
}
