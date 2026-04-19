import Modal from "../../../common/Modal.jsx";
import { useState } from "react";

export default function NewFolderModal({
                                       isOpen,
                                       setOpen,
                                       onSave,
                                   }) {
    const [value, setValue] = useState("");

    return (
        <Modal
            isOpen={isOpen}
            setOpen={setOpen}
            title="폴더를 생성하시겠습니까?"
            footer={
                <div className="flex gap-2 mt-4">
                    <button
                        className="flex-1 bg-gray-200 py-2 rounded-md"
                        onClick={() => setOpen(false)}
                    >
                        취소
                    </button>

                    <button
                        className="flex-1 bg-primary text-white py-2 rounded-md"
                        onClick={() => {
                            onSave?.(value);
                            setOpen(false);
                        }}
                    >
                        생성
                    </button>
                </div>
            }
        >
            {/*  여기 = 제목과 버튼 사이 */}
            <div className="mt-3">
                <input
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    className="w-full border rounded-md p-2"
                    placeholder="폴더 이름을 입력하세요"
                />
            </div>
        </Modal>
    );
}