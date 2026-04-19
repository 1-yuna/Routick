import { createPortal } from "react-dom";

export default function Modal({
                                  isOpen,
                                  setOpen,
                                  title,
                                  children,
                                  footer,
                              }) {
    if (!isOpen) return null;

    return createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center">

            {/* backdrop */}
            <div
                className="absolute inset-0 bg-black/40"
                onClick={() => setOpen(false)}
            />

            {/* box */}
            <div className="relative bg-white w-80 rounded-xl p-5 z-[10000]">

                {title && (
                    <p className="font-bold text-lg mb-4">
                        {title}
                    </p>
                )}

                {/* body */}
                {children}

                {/* footer */}
                {footer}

            </div>
        </div>,
        document.body
    );
}