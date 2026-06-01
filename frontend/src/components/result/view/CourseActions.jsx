import FullWidthButton from '../../../common/button/FullWidthButton.jsx';

// 결과 페이지 - 코스 액션 버튼 (장소 추가 / 편집 / 저장하기)
export default function CourseActions({ onAdd, onEdit, onSave }) {
  return (
    <div className="flex flex-col gap-3">
      {/*장소 추가 / 편집*/}
      <div className="flex gap-3">
        <button
          className="flex-1 h-10 rounded-[5px] border border-line2 text-12-sb text-gray2"
          onClick={onAdd}
        >
          장소 추가
        </button>
        <button
          className="flex-1 h-10 rounded-[5px] border border-line2 text-12-sb text-gray2"
          onClick={onEdit}
        >
          편집
        </button>
      </div>

      {/*저장하기*/}
      <FullWidthButton
        text="저장하기"
        className="bg-primary rounded-[5px]"
        onClick={onSave}
      />
    </div>
  );
}
