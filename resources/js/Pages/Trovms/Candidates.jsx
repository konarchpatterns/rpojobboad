import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link, router } from '@inertiajs/react';
import { useState, useEffect } from 'react';
import { Search, Filter, User, Mail, Phone, Award, ArrowLeft } from 'lucide-react';

export default function Candidates({ candidates, filters, experienceLevels }) {
    const [searchTerm, setSearchTerm] = useState(filters.search || '');
    const [expFilter, setExpFilter] = useState(filters.years_exp || '');

    const handleFilter = () => {
        router.get(route('trovms.candidates'), {
            search: searchTerm,
            years_exp: expFilter,
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
        if (expFilter !== (filters.years_exp || '')) {
            handleFilter();
        }
    }, [expFilter]);

    return (
        <AuthenticatedLayout
            header={
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Link href={route('dashboard')} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                            <ArrowLeft className="h-5 w-5 text-zinc-400" />
                        </Link>
                        <h2 className="font-semibold text-xl text-zinc-100 leading-tight">AHSA Candidates</h2>
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
                                className="bg-zinc-900/50 border border-zinc-800 text-zinc-200 text-sm rounded-lg pl-10 pr-4 py-2 appearance-none focus:ring-zinc-700 focus:border-zinc-700 transition-all cursor-pointer min-w-[160px]"
                                value={expFilter}
                                onChange={(e) => setExpFilter(e.target.value)}
                            >
                                <option value="">All Experience</option>
                                {experienceLevels.map(lvl => (
                                    <option key={lvl} value={lvl}>{lvl}</option>
                                ))}
                            </select>
                            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500 pointer-events-none" />
                        </div>
                    </div>
                </div>
            }
        >
            <Head title="AHSA Candidates" />

            <div className="nextjs-card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-zinc-800 bg-zinc-900/30">
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Number</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Candidate Name</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Contact Info</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Experience</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Selling Points</th>
                                <th className="px-6 py-4 text-sm font-semibold text-zinc-400">Last Updated</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800/50">
                            {candidates.data.length > 0 ? (
                                candidates.data.map((candidate) => (
                                    <tr key={candidate.id} className="hover:bg-zinc-800/20 transition-colors">
                                        <td className="px-6 py-4 text-sm text-zinc-400 font-mono">
                                            {candidate.candidate_number}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="h-8 w-8 rounded-full bg-zinc-800 flex items-center justify-center">
                                                    <User className="h-4 w-4 text-zinc-500" />
                                                </div>
                                                <div className="text-sm font-medium text-zinc-200">
                                                    {candidate.name}
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
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-2 text-sm text-zinc-300">
                                                    <Award className="h-3.5 w-3.5 text-yellow-500/50" />
                                                    {candidate.years_exp || 'N/A'} Total
                                                </div>
                                                {candidate.travel_exp && (
                                                    <div className="text-xs text-zinc-500 ml-5">
                                                        {candidate.travel_exp} Travel
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-xs text-zinc-400 max-w-xs truncate" title={candidate.selling_points}>
                                                {candidate.selling_points || 'No selling points listed.'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-zinc-500">
                                            {new Date(candidate.last_updated).toLocaleDateString()}
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
