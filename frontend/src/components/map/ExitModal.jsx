import Modal from "../../common/Modal.jsx";

export default function ExitModal({
                                           isOpen,
                                           setOpen,
                                           onExit,
                                       }) {

    return (
        <Modal
            isOpen={isOpen}
            setOpen={setOpen}
            title="종료하시겠습니까?"
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
                            onExit?.();
                            setOpen(false);
                        }}
                    >
                        종료
                    </button>
                </div>
            }
        >
        </Modal>
    );
}