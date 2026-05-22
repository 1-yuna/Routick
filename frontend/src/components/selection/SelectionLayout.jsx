import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import PromptText from '../../common/text/PromptText.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';

// 선택 페이지 공통 레이아웃
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
}) {
  const navigate = useNavigate();

  return (
    <div className="pt-12 px-6 h-screen pb-28 flex flex-col bg-default">
      <TopBar
        className="text-primary text-16-sb"
        text={`${step}/8`}
        onClick={() => (url ? navigate(url) : navigate(-1))}
      >
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="flex flex-col w-full gap-11">
        <PromptText icon={icon} text1={text1} text2={text2} subText={subText} />
        {children}
      </div>

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
