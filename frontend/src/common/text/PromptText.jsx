// 선택 페이지 - 질문 문구 (이모지 + 텍스트 + 서브텍스트)
// subText 있으면 상단 패딩 줄여서 전체 레이아웃 균형 유지
export default function PromptText({ text1, text2, icon, subText }) {
  return (
    <div
      className={`flex flex-col items-center gap-2 ${subText ? 'pt-[17px]' : 'pt-8'}`}
    >
      {/*이모지*/}
      <p className="text-36-sb">{icon}</p>

      {/*질문 텍스트*/}
      <div className="flex flex-col items-center text-16-sb text-black1">
        <p>{text1}</p>
        <p>{text2}</p>

        {/*다중 선택 안내 등 서브텍스트*/}
        <p className="text-12-rg text-gray2">{subText}</p>
      </div>
    </div>
  );
}
