// 선택 - 질문 문구
export default function PromptText({ text1, text2, icon }) {
  return (
    <div className="pt-8 flex flex-col items-center gap-2">
      <p className="text-36-sb">{icon}</p>
      <div className="flex flex-col items-center text-16-sb text-black1">
        <p>{text1}</p>
        <p>{text2}</p>
      </div>
    </div>
  );
}
