import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { Briefcase, Building2, Calendar, MapPin, Tag, Clock, ChevronLeft, ChevronRight, Search, Filter, X, Users, DollarSign, ExternalLink } from 'lucide-react';
import { useState, useEffect, useCallback, useRef } from 'react';

export default function Index({ jobs, filters, statuses, locations }) {
    const [search, setSearch] = useState(filters.search || '');
    const [status, setStatus] = useState(filters.status || '');
    const [location, setLocation] = useState(filters.location || '');
    const firstRender = useRef(true);

    useEffect(() => {
        if (firstRender.current) {
            firstRender.current = false;
            return;
        }

        const timer = setTimeout(() => {
            router.get(route('saint-francis.index'), {
                search,
                status,
                location
            }, {
                preserveState: true,
                replace: true,
            });
        }, 300);

        return () => clearTimeout(timer);
    }, [search, status, location]);

    const handleReset = () => {
        setSearch('');
        setStatus('');
        setLocation('');
        router.get(route('saint-francis.index'), {}, {
            preserveState: true,
            replace: true,
        });
    };

    return (
        <AuthenticatedLayout
            header="Saint Francis Job Listings"
        >
            <Head title="Saint Francis Jobs" />

            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Active Opportunities</h2>
                        <p className="text-sm text-zinc-400 mt-1">
                            Showing {jobs.from}-{jobs.to} of {jobs.total} jobs from Saint Francis.
                        </p>
                    </div>
                </div>

                {/* Filters */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-4 w-4 text-zinc-500" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search position, location, ID..."
                            className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-lg bg-zinc-950 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-transparent text-sm transition-all"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Filter className="h-4 w-4 text-zinc-500" />
                        </div>
                        <select
                            className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-lg bg-zinc-950 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-transparent text-sm appearance-none transition-all"
                            value={status}
                            onChange={(e) => setStatus(e.target.value)}
                        >
                            <option value="">All Statuses</option>
                            {statuses.map((s) => (
                                <option key={s} value={s}>{s}</option>
                            ))}
                        </select>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <MapPin className="h-4 w-4 text-zinc-500" />
                        </div>
                        <select
                            className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-lg bg-zinc-950 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-transparent text-sm appearance-none transition-all"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                        >
                            <option value="">All Locations</option>
                            {locations.map((l) => (
                                <option key={l} value={l}>{l}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-center gap-2">
                        {(search || status || location) && (
                            <button
                                onClick={handleReset}
                                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 border border-zinc-800 rounded-lg bg-zinc-900 text-zinc-300 hover:bg-zinc-800 hover:text-white transition-all text-sm font-medium"
                            >
                                <X className="h-4 w-4" />
                                Clear
                            </button>
                        )}
                    </div>
                </div>

                <div className="nextjs-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-zinc-800 bg-zinc-900/50">
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Job Details</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Location</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Status</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Applicants</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Pay Rate</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Updated</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {jobs.data.map((job) => (
                                    <tr key={job.job_id} className="hover:bg-zinc-900/40 transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-semibold text-zinc-100 group-hover:text-white transition-colors">
                                                    {job.position || 'N/A'}
                                                </span>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <span className="text-xs text-zinc-500 flex items-center gap-1">
                                                        <Tag className="h-3 w-3" />
                                                        ID: {job.job_id}
                                                    </span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                <MapPin className="h-3.5 w-3.5 text-zinc-500" />
                                                {job.location || 'N/A'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                                                job.status?.toLowerCase().includes('active') 
                                                    ? 'bg-green-500/10 text-green-400 ring-green-500/20' 
                                                    : 'bg-zinc-500/10 text-zinc-400 ring-zinc-500/20'
                                            }`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5 text-sm text-zinc-300">
                                            <div className="flex items-center gap-2">
                                                <Users className="h-3.5 w-3.5 text-zinc-500" />
                                                {job.applicants || '0'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-sm text-zinc-300">
                                            <div className="flex items-center gap-2">
                                                <DollarSign className="h-3.5 w-3.5 text-zinc-500" />
                                                {job.pay_rate || 'N/A'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-sm text-zinc-400">
                                            <div className="flex items-center gap-2">
                                                <Clock className="h-3.5 w-3.5 text-zinc-500" />
                                                {job.last_updated ? new Date(job.last_updated).toLocaleDateString() : 'N/A'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <Link 
                                                href={route('all-jobs.show', { portal: 'Saint Francis', id: job.job_id })}
                                                className="text-zinc-500 hover:text-blue-400 transition-colors"
                                                title="View Details"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/30 flex items-center justify-between">
                        <div className="flex flex-1 justify-between sm:hidden">
                            {jobs.prev_page_url ? (
                                <Link
                                    href={jobs.prev_page_url}
                                    className="nextjs-button-secondary py-1 text-xs"
                                >
                                    Previous
                                </Link>
                            ) : (
                                <span className="nextjs-button-secondary opacity-50 cursor-not-allowed py-1 text-xs">Previous</span>
                            )}
                            {jobs.next_page_url ? (
                                <Link
                                    href={jobs.next_page_url}
                                    className="nextjs-button-secondary py-1 text-xs"
                                >
                                    Next
                                </Link>
                            ) : (
                                <span className="nextjs-button-secondary opacity-50 cursor-not-allowed py-1 text-xs">Next</span>
                            )}
                        </div>
                        <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                            <div>
                                <p className="text-xs text-zinc-500">
                                    Page <span className="font-medium text-zinc-300">{jobs.current_page}</span> of <span className="font-medium text-zinc-300">{jobs.last_page}</span>
                                </p>
                            </div>
                            <div>
                                <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                                    {jobs.links.map((link, index) => (
                                        link.url ? (
                                            <Link
                                                key={index}
                                                href={link.url}
                                                dangerouslySetInnerHTML={{ __html: link.label }}
                                                className={`relative inline-flex items-center px-3 py-1.5 text-xs font-medium focus:z-20 transition-all duration-200 ${
                                                    link.active 
                                                        ? 'z-10 bg-zinc-50 text-zinc-950 focus-visible:outline-none' 
                                                        : 'text-zinc-400 ring-1 ring-inset ring-zinc-800 hover:bg-zinc-800 focus:outline-offset-0'
                                                } ${index === 0 ? 'rounded-l-md' : ''} ${index === jobs.links.length - 1 ? 'rounded-r-md' : ''}`}
                                            />
                                        ) : (
                                            <span
                                                key={index}
                                                dangerouslySetInnerHTML={{ __html: link.label }}
                                                className={`relative inline-flex items-center px-3 py-1.5 text-xs font-medium text-zinc-600 ring-1 ring-inset ring-zinc-800 ${index === 0 ? 'rounded-l-md' : ''} ${index === jobs.links.length - 1 ? 'rounded-r-md' : ''}`}
                                            />
                                        )
                                    ))}
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
