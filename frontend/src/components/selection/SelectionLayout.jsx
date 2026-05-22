import { useNavigate } from 'react-router-dom';
import TopBar from '../../common/bar/TopBar.jsx';
import PromptText from '../../common/text/PromptText.jsx';
import FullWidthButton from '../../common/button/FullWidthButton.jsx';
import LeftIcon from '../../assets/icons/left.svg?react';

// CourseStepLayout.jsx
export default function SelectionLayout({
  step,
  icon,
  text1,
  text2,
  children,
  onNext,
}) {
  const navigate = useNavigate();

  return (
    <div className="pt-12 px-6 h-screen pb-28 flex flex-col bg-default">
      <TopBar
        className="text-primary text-16-sb"
        text={`${step}/8`}
        onClick={() => navigate(-1)}
      >
        <LeftIcon className="w-5 h-10 text-primary" />
      </TopBar>

      <div className="flex flex-col w-full gap-11">
        <PromptText icon={icon} text1={text1} text2={text2} />

        {children}
      </div>

      <FullWidthButton
        text="다음"
        className="bg-primary mt-auto"
        onClick={onNext}
      />
    </div>
  );
}
