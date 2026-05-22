// 선택 - 질문 문구
export default function PromptText({ text1, text2, icon, subText }) {
  return (
    <div
      className={`flex flex-col items-center gap-2 ${subText ? 'pt-[17px]' : 'pt-8'}`}
    >
      <p className="text-36-sb">{icon}</p>
      <div className="flex flex-col items-center text-16-sb text-black1">
        <p>{text1}</p>
        <p>{text2}</p>
        <p className="text-12-rg text-gray2">{subText}</p>
      </div>
    </div>
  );
}
