import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { Briefcase, Building2, Calendar, MapPin, Tag, Clock, ChevronLeft, ChevronRight, Search, Filter, X, ExternalLink } from 'lucide-react';
import { useState, useEffect, useCallback, useRef } from 'react';

export default function Index({ jobs, filters, statuses, professions }) {
    const [search, setSearch] = useState(filters.search || '');
    const [profession, setProfession] = useState(filters.profession || '');
    const firstRender = useRef(true);

    useEffect(() => {
        if (firstRender.current) {
            firstRender.current = false;
            return;
        }

        const timer = setTimeout(() => {
            router.get(route('bluesky.index'), {
                search,
                profession
            }, {
                preserveState: true,
                replace: true,
            });
        }, 300);

        return () => clearTimeout(timer);
    }, [search, profession]);

    const handleReset = () => {
        setSearch('');
        setProfession('');
        router.get(route('bluesky.index'), {}, {
            preserveState: true,
            replace: true,
        });
    };

    return (
        <AuthenticatedLayout
            header="Bluesky Job Listings"
        >
            <Head title="Bluesky Jobs" />

            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Active Opportunities</h2>
                        <p className="text-sm text-zinc-400 mt-1">
                            Showing {jobs.from}-{jobs.to} of {jobs.total} jobs from Trovms.
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
                            placeholder="Search position, company, ID..."
                            className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-lg bg-zinc-950 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-transparent text-sm transition-all"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>

                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Filter className="h-4 w-4 text-zinc-500" />
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Building2 className="h-4 w-4 text-zinc-500" />
                        </div>
                        <select
                            className="block w-full pl-10 pr-3 py-2 border border-zinc-800 rounded-lg bg-zinc-950 text-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-700 focus:border-transparent text-sm appearance-none transition-all"
                            value={profession}
                            onChange={(e) => setProfession(e.target.value)}
                        >
                            <option value="">All Professions</option>
                            {professions.map((s) => (
                                <option key={s} value={s}>{s}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-center gap-2">
                        {(search || profession) && (
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
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Facility</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Unit</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Start Date - End Date</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">State</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">City</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Shift</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Reason</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Duration</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Last Seen</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {jobs.data.map((job) => (
                                    <tr key={job.id} className="hover:bg-zinc-900/40 transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-semibold text-zinc-100 group-hover:text-white transition-colors">
                                                    {job.profession || 'N/A'}
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
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.facility || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.unit || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.start_date || 'N/A'}-{job.end_date || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.state || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.city || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.shift || 'N/A'}
                                                </div>

                                            </div>
                                        </td>


                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.reason || 'N/A'}
                                                </div>

                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Building2 className="h-3.5 w-3.5 text-zinc-500" />
                                                    {job.duration || 'N/A'}
                                                </div>

                                            </div>
                                        </td>


                                        <td className="px-6 py-5 text-sm text-zinc-400">
                                            <div className="flex items-center gap-2">
                                                <Clock className="h-3.5 w-3.5 text-zinc-500" />
                                                {new Date(job.last_seen).toLocaleDateString()}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <Link 
                                                href={route('all-jobs.show', { portal: 'Bluesky', id: job.job_id })}
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
                                                className={`relative inline-flex items-center px-3 py-1.5 text-xs font-medium focus:z-20 transition-all duration-200 ${link.active
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
