import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout';
import { Head, useForm } from '@inertiajs/react';
import { Play, Plus, Trash2, Clock, CheckCircle2, XCircle, AlertCircle, Terminal, Edit2, Save, X, Square } from 'lucide-react';
import { useState } from 'react';

export default function Index({ tasks }) {
    const [selectedTask, setSelectedTask] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [showOutputModal, setShowOutputModal] = useState(false);
    const [outputContent, setOutputContent] = useState('');

    const { data, setData, post, put, delete: destroy, processing, errors, reset } = useForm({
        name: '',
        command: '',
        expression: '0 0 * * *',
        is_active: true,
    });

    const openCreateModal = () => {
        reset();
        setSelectedTask(null);
        setShowModal(true);
    };

    const openEditModal = (task) => {
        setSelectedTask(task);
        setData({
            name: task.name,
            command: task.command,
            expression: task.expression,
            is_active: task.is_active,
        });
        setShowModal(true);
    };

    const openOutputModal = (output) => {
        setOutputContent(output);
        setShowOutputModal(true);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (selectedTask) {
            put(route('scheduler.update', selectedTask.id), {
                onSuccess: () => setShowModal(false),
            });
        } else {
            post(route('scheduler.store'), {
                onSuccess: () => setShowModal(false),
            });
        }
    };

    const handleDelete = (id) => {
        if (confirm('Are you sure you want to delete this task?')) {
            destroy(route('scheduler.destroy', id));
        }
    };

    const handleRun = (id) => {
        post(route('scheduler.run', id));
    };

    const handleStop = (id) => {
        if (confirm('Are you sure you want to stop this task?')) {
            post(route('scheduler.stop', id));
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'success':
                return <span className="inline-flex items-center gap-1.5 rounded-md bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-400 ring-1 ring-inset ring-emerald-500/20"><CheckCircle2 className="h-3 w-3" /> Success</span>;
            case 'failed':
                return <span className="inline-flex items-center gap-1.5 rounded-md bg-rose-500/10 px-2 py-1 text-xs font-medium text-rose-400 ring-1 ring-inset ring-rose-500/20"><XCircle className="h-3 w-3" /> Failed</span>;
            case 'running':
                return <span className="inline-flex items-center gap-1.5 rounded-md bg-blue-500/10 px-2 py-1 text-xs font-medium text-blue-400 ring-1 ring-inset ring-blue-500/20 animate-pulse"><Clock className="h-3 w-3" /> Running</span>;
            case 'pending':
                return <span className="inline-flex items-center gap-1.5 rounded-md bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-400 ring-1 ring-inset ring-amber-500/20"><Clock className="h-3 w-3" /> Pending</span>;
            default:
                return <span className="inline-flex items-center gap-1.5 rounded-md bg-zinc-500/10 px-2 py-1 text-xs font-medium text-zinc-400 ring-1 ring-inset ring-zinc-500/20">Idle</span>;
        }
    };

    return (
        <AuthenticatedLayout header="Task Scheduler">
            <Head title="Scheduler" />

            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Automated Scripts</h2>
                        <p className="text-sm text-zinc-400 mt-1">
                            Manage and monitor your Python scrapers and background tasks.
                        </p>
                    </div>
                    <button
                        onClick={openCreateModal}
                        className="inline-flex items-center gap-2 rounded-lg bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-white transition-colors"
                    >
                        <Plus className="h-4 w-4" />
                        New Task
                    </button>
                </div>

                <div className="nextjs-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-zinc-800 bg-zinc-900/50">
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Task Name</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Command</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Schedule</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Status</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400">Last Run</th>
                                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-zinc-400 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {tasks.map((task) => (
                                    <tr key={task.id} className="hover:bg-zinc-900/40 transition-colors group">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-semibold text-zinc-100">{task.name}</span>
                                                {!task.is_active && <span className="text-[10px] text-rose-500 font-medium">Inactive</span>}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <code className="text-xs bg-zinc-800 px-2 py-1 rounded text-zinc-300 font-mono">
                                                {task.command}
                                            </code>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="text-xs text-zinc-300 font-mono">{task.expression}</span>
                                                <span className="text-[10px] text-zinc-500">Next: {task.next_run_at || 'N/A'}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            {getStatusBadge(task.status)}
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col text-xs text-zinc-400">
                                                <span>{task.last_run_at ? new Date(task.last_run_at).toLocaleString() : 'Never'}</span>
                                                {task.last_output && (
                                                    <button 
                                                        onClick={() => openOutputModal(task.last_output)}
                                                        className="text-[10px] text-zinc-500 hover:text-zinc-200 underline text-left"
                                                    >
                                                        View Output
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right space-x-2">
                                            {task.status === 'running' || task.status === 'pending' ? (
                                                <button
                                                    onClick={() => handleStop(task.id)}
                                                    className="p-2 text-rose-400 hover:text-rose-300 transition-colors rounded-lg hover:bg-rose-500/10"
                                                    title="Stop Task"
                                                >
                                                    <Square className="h-4 w-4 fill-current" />
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => handleRun(task.id)}
                                                    className="p-2 text-zinc-400 hover:text-emerald-400 transition-colors rounded-lg hover:bg-emerald-500/10"
                                                    title="Run Now"
                                                >
                                                    <Play className="h-4 w-4" />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => openEditModal(task)}
                                                className="p-2 text-zinc-400 hover:text-blue-400 transition-colors rounded-lg hover:bg-blue-500/10"
                                                title="Edit"
                                            >
                                                <Edit2 className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(task.id)}
                                                className="p-2 text-zinc-400 hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-500/10"
                                                title="Delete"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {tasks.length === 0 && (
                                    <tr>
                                        <td colSpan="6" className="px-6 py-10 text-center text-zinc-500 text-sm">
                                            No scheduled tasks found. Create your first task to get started.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Create/Edit Modal */}
            {showModal && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                    <div className="bg-zinc-950 border border-zinc-800 w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl">
                        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
                            <h3 className="text-lg font-bold">{selectedTask ? 'Edit Task' : 'New Task'}</h3>
                            <button onClick={() => setShowModal(false)} className="text-zinc-500 hover:text-zinc-200">
                                <X className="h-5 w-5" />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Task Name</label>
                                <input
                                    type="text"
                                    value={data.name}
                                    onChange={e => setData('name', e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-zinc-200 focus:ring-2 focus:ring-zinc-700 outline-none transition-all"
                                    placeholder="e.g. Westway Data Scraper"
                                    required
                                />
                                {errors.name && <p className="text-rose-500 text-xs mt-1">{errors.name}</p>}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Command / Script Path</label>
                                <input
                                    type="text"
                                    value={data.command}
                                    onChange={e => setData('command', e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-zinc-200 font-mono text-sm focus:ring-2 focus:ring-zinc-700 outline-none transition-all"
                                    placeholder="storage/app/python/westway/data.py"
                                    required
                                />
                                {errors.command && <p className="text-rose-500 text-xs mt-1">{errors.command}</p>}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-zinc-400 mb-1">Cron Expression</label>
                                <input
                                    type="text"
                                    value={data.expression}
                                    onChange={e => setData('expression', e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-zinc-200 font-mono text-sm focus:ring-2 focus:ring-zinc-700 outline-none transition-all"
                                    placeholder="* * * * *"
                                    required
                                />
                                <p className="text-[10px] text-zinc-500 mt-1">
                                    Format: minute hour day month weekday. Use "0 0 * * *" for daily at midnight.
                                </p>
                                {errors.expression && <p className="text-rose-500 text-xs mt-1">{errors.expression}</p>}
                            </div>
                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="is_active"
                                    checked={data.is_active}
                                    onChange={e => setData('is_active', e.target.checked)}
                                    className="h-4 w-4 rounded border-zinc-800 bg-zinc-900 text-zinc-100 focus:ring-zinc-700"
                                />
                                <label htmlFor="is_active" className="text-sm font-medium text-zinc-400">Task is active</label>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 px-4 py-2 border border-zinc-800 rounded-lg text-sm font-medium hover:bg-zinc-900 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={processing}
                                    className="flex-1 px-4 py-2 bg-zinc-100 text-zinc-950 rounded-lg text-sm font-bold hover:bg-white transition-colors disabled:opacity-50"
                                >
                                    {processing ? 'Saving...' : 'Save Task'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Output Modal */}
            {showOutputModal && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                    <div className="bg-zinc-950 border border-zinc-800 w-full max-w-3xl rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[80vh]">
                        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/50">
                            <div className="flex items-center gap-2">
                                <Terminal className="h-5 w-5 text-zinc-400" />
                                <h3 className="text-lg font-bold">Execution Logs</h3>
                            </div>
                            <button onClick={() => setShowOutputModal(false)} className="text-zinc-500 hover:text-zinc-200">
                                <X className="h-5 w-5" />
                            </button>
                        </div>
                        <div className="p-6 overflow-y-auto bg-black font-mono text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">
                            {outputContent || 'No output available.'}
                        </div>
                        <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900/50 flex justify-end">
                            <button
                                onClick={() => setShowOutputModal(false)}
                                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm font-medium transition-colors"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </AuthenticatedLayout>
    );
}
