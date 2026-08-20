import { useState, type ReactNode } from "react";
import type { CalendarMonth, Note, Todo } from "./types";

export function Spinner() { return <div className="spinner" aria-label="Loading" />; }
export function ErrorState({ message }: { message: string }) { return <div className="error-box">{message}</div>; }
export function EmptyState({ children }: { children: ReactNode }) { return <div className="empty-state">{children}</div>; }

export function TodoCard({ todo, onComplete, onMiss, onEdit, onDelete, canComplete = true, canMiss = true }: { todo: Todo; onComplete: () => void; onMiss: (reason: string) => void; onEdit: () => void; onDelete: () => void; canComplete?: boolean; canMiss?: boolean }) {
  const [showMiss, setShowMiss] = useState(false);
  const [reasonChoice, setReasonChoice] = useState("");
  const [customReason, setCustomReason] = useState("");
  const reason = reasonChoice === "Other" ? customReason : reasonChoice;
  const terminal = todo.status !== "pending";
  return <article className={`todo-card ${todo.status}`}>
    <div className="todo-main"><span className={`priority-dot ${todo.priority}`} /> <div><h3>{todo.title}</h3>{todo.description && <p>{todo.description}</p>}</div></div>
    <div className="todo-meta"><span className={`badge ${todo.status}`}>{todo.status}</span><span className={`priority ${todo.priority}`}>{todo.priority} priority</span>{todo.carried_from_date && <span className="carried-badge">↪ Carried from {new Date(`${todo.carried_from_date}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>}</div>
    {!terminal && <div className="todo-actions">{canComplete && <button className="button primary small" onClick={() => window.confirm("Did you actually complete this Todo?") && onComplete()}>Complete</button>}{canMiss && <button className="button subtle small" onClick={() => setShowMiss(true)}>Miss</button>}<button className="text-button" onClick={onEdit}>Edit</button><button className="text-button danger-text" onClick={onDelete}>Delete</button></div>}
    {terminal && <div className="todo-actions"><button className="text-button" onClick={onDelete}>Delete</button>{todo.status === "missed" && <span className="miss-reason">Reason: {todo.miss_reason}</span>}</div>}
    {showMiss && <div className="inline-dialog"><strong>Be honest. It’s okay to miss a Todo, but tell yourself why.</strong><select value={reasonChoice} onChange={e => setReasonChoice(e.target.value)}><option value="">Choose a reason</option><option>Not enough time</option><option>Unexpected work</option><option>Lost focus</option><option>Too difficult</option><option>Poor planning</option><option>Other</option></select>{reasonChoice === "Other" && <input placeholder="Tell yourself why" value={customReason} onChange={e => setCustomReason(e.target.value)} />}{reason && <p className="warning">This will cost you 7 points.</p>}<div><button className="button danger small" disabled={!reason.trim()} onClick={() => { onMiss(reason); setShowMiss(false); }}>Confirm miss</button><button className="text-button" onClick={() => setShowMiss(false)}>Cancel</button></div></div>}
  </article>;
}

export function NoteCard({ note, onEdit, onDelete }: { note: Note; onEdit: () => void; onDelete: () => void }) { return <article className="note-card"><div><h3>{note.title}</h3><p>{note.content}</p></div><div className="note-actions"><button className="text-button" onClick={onEdit}>Edit</button><button className="text-button danger-text" onClick={onDelete}>Delete</button></div></article>; }

export function StatCard({ label, value, accent = "" }: { label: string; value: string | number; accent?: string }) { return <div className="stat-card"><span>{label}</span><strong className={accent}>{value}</strong></div>; }

export function CalendarView({ calendar, selectedDate, onSelect }: { calendar: CalendarMonth; selectedDate: string; onSelect: (date: string) => void }) {
  const firstDay = (new Date(calendar.year, calendar.month - 1, 1).getDay() + 6) % 7;
  return <div className="calendar-grid">{["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map(day => <div className="calendar-weekday" key={day}>{day}</div>)}{Array.from({ length: firstDay }).map((_, index) => <div className="calendar-empty" key={`empty-${index}`} />)}{calendar.days.map(day => <button key={day.date} className={`calendar-day ${selectedDate === day.date ? "selected" : ""}`} onClick={() => onSelect(day.date)}><span>{Number(day.date.slice(-2))}</span>{day.todo_count > 0 && <div className="calendar-indicators">{day.pending_count > 0 && <i className="pending" />}{day.completed_count > 0 && <i className="completed" />}{day.missed_count > 0 && <i className="missed" />}</div>}<small>{day.todo_count || ""}</small></button>)}</div>;
}

export function CarryForwardDialog({ todos, onMove, onKeep, onCancel }: { todos: Todo[]; onMove: (ids: string[]) => void; onKeep: () => void; onCancel: () => void }) {
  const [selected, setSelected] = useState<string[]>(todos.map(todo => todo.id));
  const toggle = (id: string) => setSelected(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id]);
  return <div className="modal-backdrop"><div className="modal carry-dialog"><div className="modal-heading"><div><div className="eyebrow">HONEST REVIEW</div><h2>{todos.length} unfinished Todo{todos.length === 1 ? "" : "s"}</h2></div><button className="close-button" onClick={onCancel}>×</button></div><p className="muted">Move selected Todos to tomorrow? Nothing is awarded for moving them.</p><div className="carry-list">{todos.map(todo => <label className="carry-item" key={todo.id}><input type="checkbox" checked={selected.includes(todo.id)} onChange={() => toggle(todo.id)} /><span>{todo.title}</span></label>)}</div><div className="modal-actions"><button className="button subtle" onClick={onKeep}>Keep here</button><button className="button primary" disabled={!selected.length} onClick={() => onMove(selected)}>Move {selected.length || "selected"} Todo{selected.length === 1 ? "" : "s"}</button></div></div></div>;
}

export function Toast({ message, onClose }: { message: string; onClose: () => void }) { return <div className="toast" role="status">{message}<button onClick={onClose}>×</button></div>; }
