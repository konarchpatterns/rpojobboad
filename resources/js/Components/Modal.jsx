

export default function Modal({
    children,
    show = false,
    maxWidth = '2xl',
    closeable = true,
    onClose = () => {},
}) {
    const close = () => {
        if (closeable) {
            onClose();
        }
    };

    const maxWidthClass = {
        sm: 'sm:max-w-sm',
        md: 'sm:max-w-md',
        lg: 'sm:max-w-lg',
        xl: 'sm:max-w-xl',
        '2xl': 'sm:max-w-2xl',
    }[maxWidth];

    return (
        <div className={`fixed inset-0 z-50 flex items-center justify-center overflow-y-auto p-4 ${show ? 'flex' : 'hidden'}`}>
            {/* Backdrop */}
            <div 
                className="fixed inset-0 bg-black/90" 
                aria-hidden="true" 
                onClick={onClose}
            ></div>

            {/* Modal Content */}
            <div className={`relative w-full shadow-2xl bg-zinc-950 border border-zinc-800 rounded-2xl overflow-hidden ${maxWidthClass}`}>
                {children}
            </div>
        </div>
    );
}
