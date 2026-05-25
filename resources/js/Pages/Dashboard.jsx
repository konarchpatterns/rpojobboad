import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link } from '@inertiajs/react';
import { Briefcase, Users, TrendingUp, Clock } from 'lucide-react';

export default function Dashboard({ westwayCount, westwayCandidateCount, fieldglassCount, trovmsCount, ashaCandidateCount, blueskyCount, hwlCount, hwlCandidateCount, laboredgeCount, vmsCandidateCount, favoriteStaffingCount, fmsCandidateCount, medefisCount, medefisCandidateCount, saintFrancisCount, rsPrimaryCandidateCount }) {
    return (
        <AuthenticatedLayout
            header="Job Board"
        >
            <Head title="Dashboard" />

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {/* Stats Cards */}
                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">Westways</span>
                        <Briefcase className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{westwayCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{westwayCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('westway.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('westway.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">National Staffing Solutions</span>
                        <TrendingUp className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{laboredgeCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{vmsCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('laboredge.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('laboredge.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">Favourite Staffing</span>
                        <Users className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{favoriteStaffingCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{fmsCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('favorite-staffing.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('favorite-staffing.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">SHC</span>
                        <Clock className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{blueskyCount} Jobs</div>
                    <Link href={route('bluesky.index')} className="mt-1 text-xs text-green-400 font-medium hover:underline">View Now</Link>
                </div>


                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">HWLMSP</span>
                        <Clock className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{hwlCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{hwlCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('hwl.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('hwl.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">AHSA</span>
                        <Clock className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{trovmsCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{ashaCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('trovms.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('trovms.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">UHS</span>
                        <Clock className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{fieldglassCount} Jobs</div>
                    <Link href={route('fieldglass.index')} className="mt-1 text-xs text-green-400 font-medium hover:underline">View Now</Link>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">Medefis</span>
                        <Briefcase className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{medefisCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{medefisCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('medefis.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('medefis.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>

                <div className="nextjs-card p-6">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-zinc-400">RS Primary</span>
                        <Users className="h-4 w-4 text-zinc-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold">{saintFrancisCount} Jobs</div>
                    <div className="mt-1 text-sm text-zinc-500 font-medium">{rsPrimaryCandidateCount} Candidates</div>
                    <div className="flex gap-4 mt-2">
                        <Link href={route('saint-francis.index')} className="text-xs text-green-400 font-medium hover:underline">View Jobs</Link>
                        <Link href={route('saint-francis.candidates')} className="text-xs text-blue-400 font-medium hover:underline">View Candidates</Link>
                    </div>
                </div>
            </div>


        </AuthenticatedLayout>
    );
}
