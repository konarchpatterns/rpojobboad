import Modal from '@/Components/Modal';
import { X, Briefcase, Building2, Calendar, Clock, DollarSign, Info, MapPin, Tag } from 'lucide-react';

export default function JobDetailModal({ show, onClose, job }) {
    if (!job) return null;

    const detail = job.details;

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
                <div className="p-8 bg-zinc-950 text-white min-h-[300px]">
                    {detail ? (
                        <div className="space-y-6">
                            <div>
                                <h4 className="text-indigo-500 font-bold uppercase text-xs">Profession</h4>
                                <p className="text-xl font-bold">{detail.profession || job.profession || 'N/A'}</p>
                            </div>

                            <div>
                                <h4 className="text-indigo-500 font-bold uppercase text-xs">Facility</h4>
                                <p className="text-lg">{detail.facility || job.facility || 'N/A'}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <h4 className="text-indigo-500 font-bold uppercase text-xs">Status</h4>
                                    <p>{detail.status || job.status || 'N/A'}</p>
                                </div>
                                <div>
                                    <h4 className="text-indigo-500 font-bold uppercase text-xs">Specialty</h4>
                                    <p>{detail.specialty || job.specialty || 'N/A'}</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <h4 className="text-indigo-500 font-bold uppercase text-xs">Dates</h4>
                                    <p>{detail.start_date} - {detail.end_date || 'N/A'}</p>
                                </div>
                                <div>
                                    <h4 className="text-indigo-500 font-bold uppercase text-xs">Bill Rate</h4>
                                    <p className="text-emerald-400 font-bold">{'$' + detail.bill_rate || 'N/A'}</p>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-zinc-800">
                                <h4 className="text-indigo-500 font-bold uppercase text-xs mb-2">Description</h4>
                                <p className="text-zinc-300 whitespace-pre-wrap">{detail.description || 'No description provided.'}</p>
                            </div>

                            <div className="pt-4 text-[10px] text-zinc-500">
                                Scraped at: {new Date(detail.scraped_at).toLocaleString()}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-20">
                            <Info className="h-12 w-12 text-zinc-700 mx-auto mb-4" />
                            <p className="text-xl font-bold text-zinc-400">No details available for this job.</p>
                            <p className="text-zinc-600 mt-2 text-sm text-balance">This could mean the job details haven't been scraped yet or the link is no longer active.</p>
                            <p className="text-zinc-700 mt-4 text-xs font-mono">Job ID: {job.job_id}</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-zinc-800 flex justify-end bg-zinc-900/50">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-bold transition-colors text-sm"
                    >
                        Close
                    </button>
                </div>
            </div>
        </Modal>
    );
}
