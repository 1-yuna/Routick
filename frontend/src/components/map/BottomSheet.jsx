import { Sheet } from "react-modal-sheet";

export default function BottomSheet({ children }) {
    return (
        <Sheet
            style={{ zIndex: 10 }}
            isOpen={true}
            snapPoints={[0.2, 0.7, 1]}
            initialSnap={1}
            //disableDrag={true}

        >
            <Sheet.Container>
                <Sheet.Header className="flex justify-center py-2">
                    <div className="w-10 h-1.5 bg-gray-300 rounded-full" />
                </Sheet.Header>

                <Sheet.Content>
                    <div className="px-5 pb-10 overflow-y-auto">
                        {children}
                    </div>
                </Sheet.Content>
            </Sheet.Container>
        </Sheet>
    );
}