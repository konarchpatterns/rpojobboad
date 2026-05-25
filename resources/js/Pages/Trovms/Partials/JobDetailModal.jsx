import Modal from '@/Components/Modal';
import { X, Briefcase, Building2, Calendar, Clock, DollarSign, Info, MapPin, Tag, FileText } from 'lucide-react';

export default function JobDetailModal({ show, onClose, job }) {
    if (!job) return null;

    // description and details_json are directly on the job object for Trovms
    const description = job.description;
    const detailsJson = job.details_json;

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
                            <p className="text-xs text-zinc-400 font-medium">ID: {job.job_id}</p>
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
                <div className="p-8 bg-zinc-950 text-white min-h-[300px] max-h-[70vh] overflow-y-auto custom-scrollbar">
                    <div className="space-y-8">
                        {/* Primary Info */}
                        <div>
                            <h4 className="text-indigo-400 font-bold uppercase text-[10px] tracking-wider mb-1">Position & Profession</h4>
                            <p className="text-2xl font-bold text-white">{job.profession || 'N/A'}</p>
                            <p className="text-zinc-400 text-sm mt-1">{job.specialty || 'N/A'}</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
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
                                        <MapPin className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Location</h4>
                                        <p className="text-sm font-medium">{job.city ? `${job.city}, ${job.state}` : job.state || 'N/A'}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <Calendar className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Dates</h4>
                                        <p className="text-sm font-medium">Starts: {job.start_date || 'N/A'}</p>
                                        <p className="text-xs text-zinc-500 mt-0.5">Bid Due: {job.bid_due_date || 'N/A'}</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <div className="mt-1 p-1.5 bg-zinc-900 rounded-md border border-zinc-800">
                                        <Info className="h-3.5 w-3.5 text-zinc-400" />
                                    </div>
                                    <div>
                                        <h4 className="text-zinc-500 font-bold uppercase text-[10px] tracking-wider">Status & Type</h4>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded text-[10px] font-bold uppercase">
                                                {job.status || 'N/A'}
                                            </span>
                                            <span className="px-2 py-0.5 bg-zinc-800 text-zinc-300 border border-zinc-700 rounded text-[10px] font-bold uppercase">
                                                {job.job_type || 'N/A'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Description */}
                        {description && (
                            <div className="pt-6 border-t border-zinc-800">
                                <div className="flex items-center gap-2 mb-3">
                                    <FileText className="h-4 w-4 text-indigo-400" />
                                    <h4 className="text-white font-bold uppercase text-xs tracking-wider">Job Description</h4>
                                </div>
                                <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800/50 text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap">
                                    {description}
                                </div>
                            </div>
                        )}

                        {/* JSON Details */}
                        {detailsJson && Object.keys(detailsJson).length > 0 && (
                            <div className="pt-6 border-t border-zinc-800">
                                <div className="flex items-center gap-2 mb-3">
                                    <Info className="h-4 w-4 text-indigo-400" />
                                    <h4 className="text-white font-bold uppercase text-xs tracking-wider">Additional Information</h4>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {Object.entries(detailsJson).map(([key, value]) => (
                                        <div key={key} className="bg-zinc-900/30 rounded-lg p-3 border border-zinc-800/30">
                                            <h5 className="text-zinc-500 font-bold uppercase text-[9px] tracking-wider mb-1">{key.replace(/_/g, ' ')}</h5>
                                            <p className="text-zinc-200 text-sm font-medium">{String(value)}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(!description && (!detailsJson || Object.keys(detailsJson).length === 0)) && (
                            <div className="text-center py-10 bg-zinc-900/20 rounded-2xl border border-dashed border-zinc-800">
                                <p className="text-zinc-500 text-sm italic">No additional details available for this listing.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-zinc-800 flex justify-end bg-zinc-900">
                    <button 
                        onClick={onClose} 
                        className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-bold text-sm transition-all border border-zinc-700"
                    >
                        Close
                    </button>
                </div>
            </div>
        </Modal>
    );
}
