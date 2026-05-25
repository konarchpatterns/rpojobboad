import Modal from '@/Components/Modal';
import { X, Briefcase, Building2, Calendar, Clock, DollarSign, Info, MapPin, Tag } from 'lucide-react';

export default function JobDetailModal({ show, onClose, job }) {
    if (!job) return null;

    const detail = job.detail;

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
                                <h4 className="text-red-500 font-bold uppercase text-xs">Position</h4>
                                <p className="text-xl font-bold">{detail.position || job.position || 'N/A'}</p>
                            </div>
                            
                            <div>
                                <h4 className="text-red-500 font-bold uppercase text-xs">Company</h4>
                                <p className="text-lg">{detail.company_name || job.company_name || 'N/A'}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <h4 className="text-red-500 font-bold uppercase text-xs">Status</h4>
                                    <p>{detail.status || job.status || 'N/A'}</p>
                                </div>
                                <div>
                                    <h4 className="text-red-500 font-bold uppercase text-xs">Pay Range</h4>
                                    <p className="text-emerald-400 font-bold">{detail.pay_range || 'N/A'}</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                                <div>
                                    <h4 className="text-red-500 font-bold uppercase text-xs">Dates</h4>
                                    <p>{detail.dates || 'N/A'}</p>
                                </div>
                                <div>
                                    <h4 className="text-red-500 font-bold uppercase text-xs">Opened</h4>
                                    <p>{detail.opened || job.opened || 'N/A'}</p>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-zinc-800">
                                <h4 className="text-red-500 font-bold uppercase text-xs mb-2">Shift Info</h4>
                                <p className="text-zinc-300">{detail.shift_info || 'N/A'}</p>
                            </div>

                            <div className="pt-6 border-t border-zinc-800">
                                <h4 className="text-red-500 font-bold uppercase text-xs mb-2">Description</h4>
                                <p className="text-zinc-300 whitespace-pre-wrap">{detail.description || 'N/A'}</p>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-20">
                            <p className="text-xl font-bold">No details available for this job.</p>
                            <p className="text-zinc-500">job_id: {job.job_id}</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-zinc-800 flex justify-end">
                    <button onClick={onClose} className="px-6 py-2 bg-zinc-800 text-white rounded font-bold">
                        Close
                    </button>
                </div>
            </div>
        </Modal>
    );
}
