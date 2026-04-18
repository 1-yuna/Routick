// components/BottomSheet.jsx
import { Sheet } from "react-modal-sheet";

export default function BottomSheet({ isOpen, setOpen, children }) {
    return (
        <Sheet
            isOpen={isOpen}
            onClose={() => setOpen(false)}
            snapPoints={[600, 400, 200, 0]}
            initialSnap={1}
        >
            <Sheet.Container>
                {/* 헤더 (드래그 핸들 영역) */}
                <Sheet.Header className="flex justify-center py-2">
                    <div className="w-10 h-1.5 bg-gray-300 rounded-full" />
                </Sheet.Header>

                {/* 내용 */}
                <Sheet.Content>
                    <div className="px-5 pb-10 pt-2 overflow-y-auto">
                        {children}
                    </div>
                </Sheet.Content>
            </Sheet.Container>

            {/* 배경 오버레이 */}
            <Sheet.Backdrop />
        </Sheet>
    );
}