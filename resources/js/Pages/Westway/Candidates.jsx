import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { useState, useEffect } from 'react';
import { Search, Filter, User, Mail, Phone, Calendar, ArrowLeft } from 'lucide-react';

export default function Candidates({ candidates, filters, statuses }) {
    const [searchTerm, setSearchTerm] = useState(filters.search || '');
    const [statusFilter, setStatusFilter] = useState(filters.status || '');

    const handleFilter = () => {
        router.get(route('westway.candidates'), {
            search: searchTerm,
            status: statusFilter,
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
        if (statusFilter !== (filters.status || '')) {
            handleFilter();
        }
    }, [statusFilter]);

    return (
        <AuthenticatedLayout
            header={
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Link href={route('dashboard')} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                            <ArrowLeft className="h-5 w-5 text-zinc-400" />
                        </Link>
                        <h2 className="font-semibold text-xl text-zinc-100 leading-tight">Westways Candidates</h2>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search candidates..."
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 w-full md:w-64 focus:ring-zinc-700 focus:border-zinc-700 transition-all"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="relative">
                            <select
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 appearance-none focus:ring-zinc-700 focus:border-zinc-700 transition-all cursor-pointer min-w-[120px]"
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                            >
                                <option value="">All Status</option>
                                {statuses.map(status => (
                                    <option key={status} value={status}>{status}</option>
                                ))}
                            </select>
                            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
                        </div>
                    </div>
                </div>
            }
        >
            <Head title="Westways Candidates" />

            <div className="nextjs-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-zinc-800 bg-zinc-900/30">
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Appl #</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Candidate Name</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Contact Info</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Location</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Status</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Availability</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/50">
                            {candidates.data.length > 0 ? (
                                candidates.data.map((candidate) => (
                                    <tr key={candidate.id} className="hover:bg-zinc-800/20 transition-colors">
                                        <td className="px-6 py-4 text-sm text-zinc-300 font-mono">
                                            {candidate.appl_id}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center">
                                                    <User className="h-4 w-4 text-zinc-500" />
                                                </div>
                                                <div>
                                                    <div className="text-sm font-medium text-zinc-200">
                                                        {candidate.first_name} {candidate.last_name}
                                                    </div>
                                                    <div className="text-xs text-zinc-500">
                                                        {candidate.company_name}
                                                    </div>
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
                                                    {candidate.cell_phone || candidate.home_phone || 'N/A'}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            {candidate.city || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
                                                candidate.status === 'Active' 
                                                    ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                                                    : 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
                                            }`}>
                                                {candidate.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-400">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="h-3 w-3" />
                                                {candidate.date_available || 'N/A'}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-zinc-500">
                                        No candidates found.
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
