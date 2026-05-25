export default function InputLabel({
    value,
    className = '',
    children,
    ...props
}) {
    return (
        <label
            {...props}
            className={
                `block text-sm font-medium text-zinc-400 mb-1.5 ` +
                className
            }
        >
            {value ? value : children}
        </label>
    );
}
