import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { useState, useEffect } from 'react';
import { Search, Filter, ExternalLink } from 'lucide-react';

export default function AllJobs({ jobs, filters }) {
    const [searchTerm, setSearchTerm] = useState(filters.search || '');
    const [selectedPortal, setSelectedPortal] = useState(filters.portal || 'All');
    
    const portals = ['All', 'Bluesky', 'Favorite Staffing', 'Fieldglass', 'HWL', 'Laboredge', 'Medefis', 'Saint Francis', 'Trovms', 'Westway'];

    const handleFilter = () => {
        router.get(route('all-jobs.index'), {
            search: searchTerm,
            portal: selectedPortal
        }, {
            preserveState: true,
            replace: true
        });
    };

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            if (searchTerm !== (filters.search || '')) {
                handleFilter();
            }
        }, 300);

        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm]);

    useEffect(() => {
        if (selectedPortal !== (filters.portal || 'All')) {
            handleFilter();
        }
    }, [selectedPortal]);

    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            handleFilter();
        }
    };

    const displayJobs = jobs?.data || [];

    return (
        <AuthenticatedLayout
            header={
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <h2 className="font-semibold text-xl text-zinc-100 leading-tight">Unified Job Board</h2>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search jobs..."
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 w-full md:w-64 focus:ring-zinc-700 focus:border-zinc-700 transition-all"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onKeyDown={handleSearch}
                            />
                        </div>
                        <div className="relative">
                            <select
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 appearance-none focus:ring-zinc-700 focus:border-zinc-700 transition-all cursor-pointer min-w-[140px]"
                                value={selectedPortal}
                                onChange={(e) => setSelectedPortal(e.target.value)}
                            >
                                {portals.map(portal => (
                                    <option key={portal} value={portal}>{portal}</option>
                                ))}
                            </select>
                            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
                        </div>
                    </div>
                </div>
            }
        >
            <Head title="All Jobs" />

            <div className="nextjs-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-zinc-800 bg-zinc-900/30">
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Job ID</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Job Title</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Dept/Facility</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">City</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">State</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Type</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Portal</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/50">
                            {displayJobs.length > 0 ? (
                                displayJobs.map((job, index) => (
                                    <tr 
                                        key={`${job.portal}-${job.job_id}-${index}`}
                                        className="hover:bg-zinc-800/20 transition-colors group"
                                    >
                                        <td className="px-6 py-4 text-sm text-zinc-300 font-mono">
                                            {job.job_id}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-200 font-medium">
                                            {job.job_title || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            {job.location || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            {job.city && job.city !== 'N/A' ? job.city : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            {job.state && job.state !== 'N/A' ? job.state : '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            {job.job_type || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPortalStyle(job.portal)}`}>
                                                {job.portal}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <Link 
                                                href={route('all-jobs.show', { portal: job.portal, id: job.job_id })}
                                                className="text-zinc-500 hover:text-blue-400 transition-colors"
                                                title="View Details"
                                            >
                                                <ExternalLink className="h-4 w-4" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="8" className="px-6 py-12 text-center text-zinc-500">
                                        <div className="flex flex-col items-center gap-2">
                                            <Search className="h-8 w-8 opacity-20" />
                                            <p>No jobs found.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Controls */}
                <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/30 flex items-center justify-between">
                    <div className="text-xs text-zinc-500">
                        Showing <span className="font-medium text-zinc-300">{jobs.from}</span> to <span className="font-medium text-zinc-300">{jobs.to}</span> of <span className="font-medium text-zinc-300">{jobs.total}</span> jobs
                    </div>
                    
                    <div className="flex items-center gap-2">
                        {jobs?.links?.map((link, i) => (
                            link.url ? (
                                <Link
                                    key={i}
                                    href={link.url}
                                    className={`px-3 py-1 text-xs rounded-md border transition-all ${
                                        link.active 
                                            ? 'bg-zinc-800 border-zinc-700 text-zinc-100 font-bold' 
                                            : 'border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-300'
                                    }`}
                                    dangerouslySetInnerHTML={{ __html: link.label }}
                                />
                            ) : (
                                <span
                                    key={i}
                                    className="px-3 py-1 text-xs rounded-md border border-transparent text-zinc-700 cursor-not-allowed"
                                    dangerouslySetInnerHTML={{ __html: link.label }}
                                />
                            )
                        ))}
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}

function getPortalStyle(portal) {
    const styles = {
        'Westway': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        'Fieldglass': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
        'HWL': 'bg-green-500/10 text-green-400 border-green-500/20',
        'Laboredge': 'bg-orange-500/10 text-orange-400 border-orange-500/20',
        'Medefis': 'bg-pink-500/10 text-pink-400 border-pink-500/20',
        'Trovms': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
        'Bluesky': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
        'Favorite Staffing': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        'Saint Francis': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };
    return styles[portal] || 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20';
}
