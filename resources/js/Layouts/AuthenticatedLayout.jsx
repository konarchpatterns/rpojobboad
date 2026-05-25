import { useState } from 'react';
import { Link, usePage } from '@inertiajs/react';
import { LayoutDashboard, User, LogOut, Menu, X, Bell } from 'lucide-react';

export default function AuthenticatedLayout({ header, children }) {
    const user = usePage().props.auth.user;
    const [showingNavigationDropdown, setShowingNavigationDropdown] = useState(false);

    return (
        <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans selection:bg-zinc-800 selection:text-zinc-50">
            {/* Top Navigation */}
            <nav className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 justify-between items-center">
                        <div className="flex items-center gap-8">
                            <Link href={route('dashboard')} className="flex items-center gap-2 group">
                                <svg viewBox="0 0 24 24" className="h-6 w-6 text-zinc-50 fill-current" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2L2 19.7h20L12 2zm0 4.5l6.5 11.2H5.5L12 6.5z" />
                                </svg>
                                <span className="text-lg font-bold tracking-tight">Patterns JobBoard</span>
                            </Link>

                            <div className="hidden space-x-6 sm:flex">
                                <Link
                                    href={route('dashboard')}
                                    className={`text-sm font-medium transition-colors hover:text-zinc-50 ${route().current('dashboard') ? 'text-zinc-50' : 'text-zinc-400'}`}
                                >
                                    Dashboard
                                </Link>
                                <Link
                                    href={route('all-jobs.index')}
                                    className={`text-sm font-medium transition-colors hover:text-zinc-50 ${route().current('all-jobs.index') ? 'text-zinc-50' : 'text-zinc-400'}`}
                                >
                                    All Jobs
                                </Link>
                                <Link
                                    href={route('all-candidates.index')}
                                    className={`text-sm font-medium transition-colors hover:text-zinc-50 ${route().current('all-candidates.index') ? 'text-zinc-50' : 'text-zinc-400'}`}
                                >
                                    All Candidates
                                </Link>
                                <Link
                                    href={route('scheduler.index')}
                                    className={`text-sm font-medium transition-colors hover:text-zinc-50 ${route().current('scheduler.index') ? 'text-zinc-50' : 'text-zinc-400'}`}
                                >
                                    Scheduler
                                </Link>

                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <button className="text-zinc-400 hover:text-zinc-50 transition-colors">
                                <Bell className="h-5 w-5" />
                            </button>

                            <div className="relative flex items-center gap-3 pl-4 border-l border-zinc-800">
                                <span className="hidden text-sm font-medium text-zinc-400 sm:inline-block">{user.name}</span>
                                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700 text-xs font-bold">
                                    {user.name.charAt(0).toUpperCase()}
                                </div>
                                <Link
                                    href={route('logout')}
                                    method="post"
                                    as="button"
                                    className="text-zinc-400 hover:text-rose-400 transition-colors"
                                >
                                    <LogOut className="h-5 w-5" />
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Page Header */}
            {header && (
                <header className="bg-zinc-950 border-b border-zinc-800">
                    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                        <h1 className="text-2xl font-bold tracking-tight text-zinc-50">{header}</h1>
                    </div>
                </header>
            )}

            {/* Main Content */}
            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                {children}
            </main>

            <footer className="mt-auto border-t border-zinc-800 py-8">
                <div className="mx-auto max-w-7xl px-4 text-center text-sm text-zinc-500 sm:px-6 lg:px-8">
                    &copy; {new Date().getFullYear()} Powerd By Patterns.
                </div>
            </footer>
        </div>
    );
}
