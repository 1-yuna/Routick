// 공통 모달 - children + 취소/확인 버튼
// confirmOnly: true면 확인 버튼만 표시
export default function BaseModal({
  children,
  onConfirm,
  onCancel,
  confirmOnly = false,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-10 w-[298px] flex flex-col">
        {/* 커스텀 컨텐츠 */}
        <div className="flex flex-col items-center gap-1 pt-8 px-5 pb-4">
          {children}
        </div>

        {/* 구분선 */}
        <div className="h-[1px] bg-line1" />

        {/* 버튼 영역 */}
        <div className="flex text-12-sb">
          {confirmOnly ? (
            <button
              onClick={onConfirm}
              className="flex-1 justify-center items-center text-primary py-3"
            >
              확인
            </button>
          ) : (
            <>
              <button
                onClick={onCancel}
                className="flex-1 justify-center items-center text-gray2 py-3"
              >
                취소
              </button>
              <div className="w-[1px] bg-line1" />
              <button
                onClick={onConfirm}
                className="flex-1 justify-center items-center text-primary py-3"
              >
                확인
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
