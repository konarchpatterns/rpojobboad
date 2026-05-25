import { Link } from '@inertiajs/react';

export default function GuestLayout({ children }) {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 px-6 py-12 selection:bg-zinc-800 selection:text-zinc-50">
            <div className="w-full sm:max-w-[400px]">
                <div className="flex flex-col items-center mb-8">
                    <Link href="/" className="flex items-center gap-2 group transition-opacity hover:opacity-80">
                        {/* Next.js style Logo (Minimalist Triangle/Shield) */}
                        <svg
                            viewBox="0 0 24 24"
                            className="h-8 w-8 text-zinc-50 fill-current"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path d="M12 2L2 19.7h20L12 2zm0 4.5l6.5 11.2H5.5L12 6.5z" />
                        </svg>
                        <span className="text-xl font-bold tracking-tight text-zinc-50">Patterns Jobboard</span>
                    </Link>
                </div>

                <div className="nextjs-card p-6 shadow-2xl sm:p-8">
                    {children}
                </div>

                <div className="mt-8 text-center text-xs text-zinc-500">
                    Built by Patterns  &copy; {new Date().getFullYear()}
                </div>
            </div>
        </div>
    );
}
