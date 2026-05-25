import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { useState, useEffect } from 'react';
import { Search, Filter, User, Mail, Phone, Calendar, ArrowLeft, Globe } from 'lucide-react';

export default function AllCandidates({ candidates, filters, portals }) {
    const [searchTerm, setSearchTerm] = useState(filters.search || '');
    const [portalFilter, setPortalFilter] = useState(filters.portal || 'All');

    const handleFilter = () => {
        router.get(route('all-candidates.index'), {
            search: searchTerm,
            portal: portalFilter,
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
        if (portalFilter !== (filters.portal || 'All')) {
            handleFilter();
        }
    }, [portalFilter]);

    return (
        <AuthenticatedLayout
            header={
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Link href={route('dashboard')} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                            <ArrowLeft className="h-5 w-5 text-zinc-400" />
                        </Link>
                        <h2 className="font-semibold text-xl text-zinc-100 leading-tight">All Candidates</h2>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search all candidates..."
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 w-full md:w-64 focus:ring-zinc-700 focus:border-zinc-700 transition-all"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="relative">
                            <select
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 appearance-none focus:ring-zinc-700 focus:border-zinc-700 transition-all cursor-pointer min-w-[160px]"
                                value={portalFilter}
                                onChange={(e) => setPortalFilter(e.target.value)}
                            >
                                <option value="All">All Portals</option>
                                {portals.map(p => (
                                    <option key={p} value={p}>{p}</option>
                                ))}
                            </select>
                            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
                        </div>
                    </div>
                </div>
            }
        >
            <Head title="All Candidates" />

            <div className="nextjs-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-zinc-800 bg-zinc-900/30">
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Portal</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Candidate Name</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Contact Info</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Last Updated</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/50">
                            {candidates.data.length > 0 ? (
                                candidates.data.map((candidate, index) => (
                                    <tr key={`${candidate.portal}-${index}`} className="hover:bg-zinc-800/20 transition-colors">
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 text-[10px] font-bold rounded uppercase tracking-wider ${
                                                candidate.portal === 'Westway' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                                                candidate.portal === 'National Staffing' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' :
                                                candidate.portal === 'Favourite Staffing' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' :
                                                candidate.portal === 'HWLMSP' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' :
                                                candidate.portal === 'AHSA' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                                                'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                            }`}>
                                                {candidate.portal}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center">
                                                    <User className="h-4 w-4 text-zinc-500" />
                                                </div>
                                                <div className="text-sm font-medium text-zinc-200">
                                                    {candidate.name || 'Unknown Candidate'}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-2 text-xs text-zinc-400">
                                                    <Mail className="h-3 w-3" />
                                                    {candidate.email || 'N/A'}
                                                </div>
                                                <div className="flex items-center gap-2 text-xs text-zinc-400">
                                                    <Phone className="h-3 w-3" />
                                                    {candidate.phone || 'N/A'}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-500">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="h-3.5 w-3.5" />
                                                {candidate.last_updated ? new Date(candidate.last_updated).toLocaleDateString() : 'N/A'}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center text-zinc-500">
                                        No candidates found across portals.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/30 flex items-center justify-between">
                    <div className="text-xs text-zinc-500">
                        Showing {candidates.from || 0} to {candidates.to || 0} of {candidates.total} candidates
                    </div>
                    <div className="flex items-center gap-2">
                        {candidates.links.map((link, i) => (
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
