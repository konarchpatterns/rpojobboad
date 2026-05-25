import Modal from '@/Components/Modal';
import { X, Briefcase, Building2, Calendar, Clock, DollarSign, Info, MapPin, Tag, FileText, UserCheck, Layers } from 'lucide-react';

export default function JobDetailModal({ show, onClose, job }) {
    if (!job) return null;

    const detailsJson = job.details_json;
    const description = detailsJson?.['Job Description Text'];

    return (
        <Modal show={show} onClose={onClose} maxWidth="2xl">
            <div className="overflow-hidden">
                {/* Header */}
                <div className="px-6 py-5 border-b border-zinc-800 flex items-center justify-between bg-zinc-900">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 bg-zinc-800 rounded-xl">
                            <Briefcase className="h-5 w-5 text-zinc-100" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white tracking-tight">Job Details</h3>
                            <p className="text-xs text-zinc-400 font-medium">ID: {job.job_number}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-lg transition-all"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Content Area */}
                <div className="p-8 bg-zinc-950 text-white min-h-[300px] max-h-[75vh] overflow-y-auto custom-scrollbar">
                    <div className="space-y-8">
                        {/* Primary Info */}
                        <div>
                            <h4 className="text-emerald-400 font-bold uppercase text-[10px] tracking-wider mb-1">Job Name & Specialty</h4>
                            <p className="text-2xl font-bold text-white leading-tight">{job.job_name || 'N/A'}</p>
                            <div className="flex items-center gap-2 mt-2">
                                <span className="text-zinc-400 text-sm">{job.specialty || 'N/A'}</span>
                                {job.sub_specialty && (
                                    <>
                                        <span className="text-zinc-700">•</span>
                                        <span className="text-zinc-500 text-sm">{job.sub_specialty}</span>
                                    </>
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-5">
                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <Building2 className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Facility</h4>
                                        <p className="text-sm font-medium">{job.facility || 'N/A'}</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <UserCheck className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Positions</h4>
                                        <p className="text-sm font-medium">{job.positions || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-5">
                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <Calendar className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Timeline</h4>
                                        <p className="text-sm font-medium">Starts: {job.start_date || 'N/A'}</p>
                                        <p className="text-xs text-zinc-500 mt-0.5">Posted: {job.posted_date || 'N/A'}</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <Layers className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Job Type</h4>
                                        <span className="inline-block mt-1 px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-[10px] font-bold uppercase">
                                            {job.job_type || 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Description from JSON */}
                        {description && (
                            <div className="pt-6 border-t border-zinc-800">
                                <div className="flex items-center gap-2 mb-3">
                                    <FileText className="h-4 w-4 text-emerald-400" />
                                    <h4 className="text-white font-bold uppercase text-xs tracking-wider">Job Description</h4>
                                </div>
                                <div className="bg-zinc-900/50 rounded-xl p-5 border border-zinc-800/50 text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap">
                                    {description}
                                </div>
                            </div>
                        )}

                        {/* JSON Details (filtering out the description since it's shown above) */}
                        {detailsJson && Object.keys(detailsJson).filter(key => key !== 'Job Description Text').length > 0 && (
                            <div className="pt-6 border-t border-zinc-800">
                                <div className="flex items-center gap-2 mb-3">
                                    <Info className="h-4 w-4 text-emerald-400" />
                                    <h4 className="text-white font-bold uppercase text-xs tracking-wider">Additional Information</h4>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {Object.entries(detailsJson)
                                        .filter(([key]) => key !== 'Job Description Text')
                                        .map(([key, value]) => (
                                            <div key={key} className="bg-zinc-900/40 rounded-lg p-3 border border-zinc-800/30 flex flex-col gap-0.5">
                                                <h5 className="text-zinc-500 font-bold uppercase text-[9px] tracking-wider">{key}</h5>
                                                <p className="text-zinc-200 text-sm font-medium">{String(value)}</p>
                                            </div>
                                        ))}
                                </div>
                            </div>
                        )}

                        {(!detailsJson || Object.keys(detailsJson).length === 0) && (
                            <div className="text-center py-12 bg-zinc-900/20 rounded-2xl border border-dashed border-zinc-800/50">
                                <Info className="h-8 w-8 text-zinc-700 mx-auto mb-3" />
                                <p className="text-zinc-500 text-sm italic">No extended details available for this job.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-zinc-800 flex justify-end bg-zinc-900">
                    <button 
                        onClick={onClose} 
                        className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-bold text-sm transition-all border border-zinc-700 shadow-lg shadow-black/20"
                    >
                        Close
                    </button>
                </div>
            </div>
        </Modal>
    );
}
