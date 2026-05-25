import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, Link } from '@inertiajs/react';
import { 
    Briefcase, 
    Building2, 
    Calendar, 
    Clock, 
    DollarSign, 
    Info, 
    MapPin, 
    Tag, 
    FileText, 
    UserCheck, 
    Layers, 
    ChevronLeft,
    Globe,
    Map
} from 'lucide-react';

export default function JobDetails({ job, portal }) {
    if (!job) return (
        <AuthenticatedLayout header="Job Not Found">
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-zinc-500">
                <Info className="h-12 w-12 opacity-20 mb-4" />
                <p className="text-xl font-medium">Job details could not be found.</p>
                <Link href={route('all-jobs.index')} className="mt-4 text-blue-400 hover:underline">
                    Return to Job Board
                </Link>
            </div>
        </AuthenticatedLayout>
    );

    // Normalize data based on portal
    const details = {
        title: job.job_title || job.job_name || job.position || job.job_class || job.profession || job.title || 'N/A',
        id: job.job_id || job.job_number || job.order_id || 'N/A',
        location: job.location || job.facility || job.site || 'N/A',
        city: job.city || 'N/A',
        state: job.state || 'N/A',
        type: job.job_type || job.order_type || 'N/A',
        status: job.status || 'Active',
        startDate: job.start_date || 'N/A',
        endDate: job.end_date || 'N/A',
        postedDate: job.posted_date || job.opened || job.posted_on || 'N/A',
        payRange: job.pay_range || (job.detail?.pay_range) || (job.details?.pay_range) || (job.detail?.bill_rate) || (job.details?.bill_rate) || (job.detail?.pay_rates ? JSON.stringify(job.detail.pay_rates) : null) || (job.details?.pay_rates ? JSON.stringify(job.details.pay_rates) : null) || job.pay_rate || 'N/A',
        description: job.description || job.detail?.description || job.details?.description || job.details_json?.['Job Description Text'] || null,
        extraInfo: job.details_json || job.details || job.detail || {},
    };

    const portalStyles = {
        'Westway': { color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20', accent: 'bg-blue-500' },
        'Fieldglass': { color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20', accent: 'bg-purple-500' },
        'HWL': { color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/20', accent: 'bg-green-500' },
        'Laboredge': { color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20', accent: 'bg-orange-500' },
        'Medefis': { color: 'text-pink-400', bg: 'bg-pink-500/10', border: 'border-pink-500/20', accent: 'bg-pink-500' },
        'Trovms': { color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20', accent: 'bg-cyan-500' },
        'Bluesky': { color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/20', accent: 'bg-indigo-500' },
        'Favorite Staffing': { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', accent: 'bg-yellow-500' },
        'Saint Francis': { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', accent: 'bg-emerald-500' },
    };

    const style = portalStyles[portal] || { color: 'text-zinc-400', bg: 'bg-zinc-500/10', border: 'border-zinc-500/20', accent: 'bg-zinc-500' };
    
    // Helper to format complex values (objects/arrays)
    const formatValue = (value) => {
        if (value === null || value === undefined) return 'N/A';
        if (typeof value !== 'object') return String(value);
        
        // If it's an object/array, render it as a list of tags or a small grid
        return (
            <div className="flex flex-wrap gap-1.5 mt-1">
                {Object.entries(value).map(([k, v]) => (
                    <div key={k} className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-800/50 border border-zinc-700/50 text-[10px]">
                        <span className="text-zinc-500 font-bold uppercase tracking-tighter">{k.replace(/_/g, ' ')}:</span>
                        <span className="text-zinc-200 font-medium">{String(v)}</span>
                    </div>
                ))}
            </div>
        );
    };

    // Special handling for pay rates display in hero
    const renderPayRange = () => {
        const pay = job.pay_range || (job.details?.pay_range) || (job.detail?.pay_range) || job.pay_rate;
        if (pay && pay !== 'N/A') return pay;

        const rates = job.details?.pay_rates || job.detail?.pay_rates;
        if (rates && typeof rates === 'object') {
            // Try to find a "Regular" or "Day" rate to show as primary
            const primaryKey = Object.keys(rates).find(k => k.toLowerCase().includes('regular') || k.toLowerCase().includes('day') || k.toLowerCase().includes('hr')) || Object.keys(rates)[0];
            return rates[primaryKey] ? `${rates[primaryKey]} (Multi-rate)` : 'Multi-rate';
        }

        return 'N/A';
    };

    return (
        <AuthenticatedLayout
            header={
                <div className="flex items-center gap-4">
                    <Link 
                        href={route('all-jobs.index')}
                        className="p-2 hover:bg-zinc-800 rounded-full transition-colors text-zinc-400 hover:text-white"
                    >
                        <ChevronLeft className="h-5 w-5" />
                    </Link>
                    <div>
                        <h2 className="font-semibold text-xl text-zinc-100 leading-tight">Job Details</h2>
                        <div className="flex items-center gap-2 mt-1">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${style.bg} ${style.color} ${style.border}`}>
                                {portal}
                            </span>
                            <span className="text-zinc-500 text-xs">ID: {details.id}</span>
                        </div>
                    </div>
                </div>
            }
        >
            <Head title={`${details.title} - ${portal}`} />

            <div className="max-w-5xl mx-auto space-y-6 pb-12">
                {/* Hero Section */}
                <div className="nextjs-card p-8 relative overflow-hidden">
                    <div className={`absolute top-0 left-0 w-1 h-full ${style.accent}`} />
                    <div className="relative z-10">
                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                            <div className="space-y-4 max-w-2xl">
                                <div>
                                    <h1 className="text-3xl font-bold text-white tracking-tight leading-tight">
                                        {details.title}
                                    </h1>
                                    <div className="flex flex-wrap items-center gap-4 mt-3 text-zinc-400">
                                        <div className="flex items-center gap-1.5">
                                            <Building2 className="h-4 w-4 text-zinc-500" />
                                            <span className="text-sm font-medium">{details.location}</span>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <MapPin className="h-4 w-4 text-zinc-500" />
                                            <span className="text-sm font-medium">{details.city}{details.state !== 'N/A' ? `, ${details.state}` : ''}</span>
                                        </div>
                                        <div className="flex items-center gap-1.5">
                                            <Tag className="h-4 w-4 text-zinc-500" />
                                            <span className="text-sm font-medium">{details.type}</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="flex flex-wrap gap-2">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${details.status?.toLowerCase().includes('active') ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'}`}>
                                        {details.status}
                                    </span>
                                    {renderPayRange() !== 'N/A' && (
                                        <div className="flex flex-col gap-2">
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 w-fit">
                                                <DollarSign className="h-3 w-3 mr-1" />
                                                {renderPayRange()}
                                            </span>
                                            {/* Show full breakdown if it's HWL multi-rate */}
                                            {(job.details?.pay_rates || job.detail?.pay_rates) && typeof (job.details?.pay_rates || job.detail?.pay_rates) === 'object' && (
                                                <div className="bg-zinc-900/40 p-3 rounded-xl border border-zinc-800/50 max-w-xl">
                                                    <p className="text-[10px] font-bold text-zinc-500 uppercase mb-2 tracking-widest">Full Rate Breakdown</p>
                                                    {formatValue(job.details?.pay_rates || job.detail?.pay_rates)}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                            
                            <div className="flex flex-col gap-3 min-w-[200px]">
                                <button className={`w-full py-2.5 px-4 rounded-xl font-bold text-sm shadow-lg shadow-black/20 transition-all hover:scale-[1.02] active:scale-[0.98] ${style.accent} text-white`}>
                                    Apply Now
                                </button>
                                <button className="w-full py-2.5 px-4 rounded-xl font-bold text-sm bg-zinc-800 text-white border border-zinc-700 hover:bg-zinc-700 transition-all">
                                    Save for Later
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Description */}
                        <div className="nextjs-card p-8">
                            <div className="flex items-center gap-2 mb-6">
                                <FileText className={`h-5 w-5 ${style.color}`} />
                                <h3 className="text-lg font-bold text-white uppercase tracking-wider">Job Description</h3>
                            </div>
                            {details.description ? (
                                <div className="prose prose-invert max-w-none text-zinc-300 leading-relaxed whitespace-pre-wrap">
                                    {details.description}
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 bg-zinc-900/30 rounded-2xl border border-dashed border-zinc-800">
                                    <Info className="h-8 w-8 text-zinc-700 mb-2" />
                                    <p className="text-zinc-500 italic">No detailed description provided for this job.</p>
                                </div>
                            )}
                        </div>

                        {/* Additional Data Sections */}
                        {Object.keys(details.extraInfo || {}).length > 0 && (
                            <div className="nextjs-card p-8">
                                <div className="flex items-center gap-2 mb-6">
                                    <Layers className={`h-5 w-5 ${style.color}`} />
                                    <h3 className="text-lg font-bold text-white uppercase tracking-wider">Additional Information</h3>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {Object.entries(details.extraInfo)
                                        .filter(([key, value]) => {
                                            // Filter out internal fields and fields we already display
                                            const skip = ['id', 'job_id', 'job_title', 'location', 'description', 'created_at', 'updated_at', 'Job Description Text'];
                                            return !skip.includes(key) && value !== null && value !== '';
                                        })
                                        .map(([key, value]) => (
                                            <div key={key} className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800/50">
                                                <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider mb-1">{key.replace(/_/g, ' ')}</h4>
                                                <div className="text-zinc-200 text-sm font-medium">
                                                    {formatValue(value)}
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Timeline Card */}
                        <div className="nextjs-card p-6">
                            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
                                <Clock className={`h-4 w-4 ${style.color}`} />
                                Timeline
                            </h3>
                            <div className="space-y-4">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-zinc-900 rounded-lg border border-zinc-800">
                                        <Calendar className="h-4 w-4 text-zinc-400" />
                                    </div>
                                    <div>
                                        <p className="text-xs text-zinc-500 uppercase font-bold tracking-tighter">Start Date</p>
                                        <p className="text-sm font-medium text-zinc-200">{details.startDate}</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-zinc-900 rounded-lg border border-zinc-800">
                                        <Calendar className="h-4 w-4 text-zinc-400" />
                                    </div>
                                    <div>
                                        <p className="text-xs text-zinc-500 uppercase font-bold tracking-tighter">End Date</p>
                                        <p className="text-sm font-medium text-zinc-200">{details.endDate}</p>
                                    </div>
                                </div>
                                <div className="pt-4 border-t border-zinc-800">
                                    <p className="text-xs text-zinc-500">
                                        Posted: <span className="text-zinc-300">{details.postedDate}</span>
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Portal Card */}
                        <div className="nextjs-card p-6">
                            <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-6 flex items-center gap-2">
                                <Globe className={`h-4 w-4 ${style.color}`} />
                                Source Portal
                            </h3>
                            <div className="flex flex-col items-center text-center gap-3">
                                <div className={`w-16 h-16 rounded-2xl ${style.bg} border ${style.border} flex items-center justify-center`}>
                                    <Briefcase className={`h-8 w-8 ${style.color}`} />
                                </div>
                                <div>
                                    <p className="text-lg font-bold text-white">{portal}</p>
                                    <p className="text-xs text-zinc-500">Job sourced from {portal} ecosystem</p>
                                </div>
                                <div className="w-full pt-4 border-t border-zinc-800">
                                    <Link 
                                        href={route('all-jobs.index', { portal })}
                                        className="text-xs font-bold text-blue-400 hover:text-blue-300 transition-colors"
                                    >
                                        View more from {portal}
                                    </Link>
                                </div>
                            </div>
                        </div>

                        {/* Location Mini-Map (Static representation) */}
                        <div className="nextjs-card p-6">
                             <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                                <Map className={`h-4 w-4 ${style.color}`} />
                                Location
                            </h3>
                            <div className="aspect-video bg-zinc-900 rounded-xl border border-zinc-800 flex items-center justify-center relative overflow-hidden">
                                <div className="absolute inset-0 opacity-20 pointer-events-none">
                                    {/* Mock grid to represent map */}
                                    <div className="w-full h-full" style={{ backgroundImage: 'radial-gradient(circle, #333 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
                                </div>
                                <div className="relative z-10 flex flex-col items-center gap-2">
                                    <div className={`p-2 rounded-full ${style.bg} border ${style.border}`}>
                                        <MapPin className={`h-5 w-5 ${style.color}`} />
                                    </div>
                                    <p className="text-[10px] text-zinc-400 text-center px-4">
                                        {details.location}<br/>
                                        {details.city}, {details.state}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AuthenticatedLayout>
    );
}
