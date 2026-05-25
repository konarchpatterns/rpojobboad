export default function Checkbox({ className = '', ...props }) {
    return (
        <input
            {...props}
            type="checkbox"
            className={
                'rounded border-white/10 bg-nexus-900 text-primary shadow-sm focus:ring-primary focus:ring-offset-nexus-950 ' +
                className
            }
        />
    );
}
