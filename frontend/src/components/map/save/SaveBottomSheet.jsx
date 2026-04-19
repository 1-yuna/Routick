import {Sheet} from "react-modal-sheet"
import {IoClose} from "react-icons/io5";
import { FiPlus } from "react-icons/fi";
import {useState} from "react";
import SaveFolderModal from "./SaveFolderModal.jsx";
import SaveItem from "./SaveItem.jsx";
import NewItem from "./NewItem.jsx";
import NewFolderModal from "./NewFolderModal.jsx";

export default function SaveBottomSheet({isOpen, setOpen}) {
    const [isSaveOpen, setIsSaveOpen] = useState(false);
    const [isFolderOpen, setIsFolderOpen] = useState(false);

    // mock
    const places = [
        { id: 1, title: "부산" },
        { id: 2, title: "서울" },
        { id: 3, title: "제주" },
    ];

    return (
        <>
        <Sheet isOpen={isOpen} onClose={() => setOpen(false)}>
            <Sheet.Container>

                <Sheet.Content>
                    <div className="p-5">

                        {/*버튼*/}
                        <button className="mb-4"
                                onClick={() => setOpen(false)}
                        >
                            <IoClose className="w-6 h-6"/>
                        </button>

                        {/*리스트*/}
                        <div className="space-y-2">
                            {places.map((place) => (
                                <SaveItem
                                    key={place.id}
                                    place={place}
                                    onClick={() => {
                                        console.log(place.title);
                                        setIsSaveOpen(true);
                                    }}
                                />
                            ))}
                        </div>

                        {/*폴더 생성*/}
                        <NewItem onClick={() => setIsFolderOpen(true)} />


                    </div>
                </Sheet.Content>
            </Sheet.Container>

            <Sheet.Backdrop/>
        </Sheet>

            <SaveFolderModal
                isOpen={isSaveOpen}
                setOpen={setIsSaveOpen}
                onSave={() => console.log("저장")}
            />

            <NewFolderModal
                isOpen={isFolderOpen}
                setOpen={setIsFolderOpen}
                onSave={(value) => console.log("폴더 생성:", value)}
            />
        </>

    );
}