import type { CalendarMonth, Dashboard, Note, Todo, Transaction, User } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  const token = localStorage.getItem("two-do-token");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Something went wrong");
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  register: (data: { name: string; email: string; password: string }) => request<{ access_token: string; user: User }>("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) => request<{ access_token: string; user: User }>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request<User>("/auth/me"),
  dashboard: () => request<Dashboard>("/dashboard"),
  todos: (date?: string) => request<Todo[]>(date ? `/todos?date=${date}` : "/todos"),
  unresolved: (date?: string) => request<Todo[]>(date ? `/todos/unresolved?date=${date}` : "/todos/unresolved"),
  calendar: (year: number, month: number) => request<CalendarMonth>(`/calendar?year=${year}&month=${month}`),
  carryForward: (todoIds: string[]) => request<Todo[]>("/todos/carry-forward", { method: "POST", body: JSON.stringify({ todo_ids: todoIds }) }),
  createTodo: (data: object) => request<Todo>("/todos", { method: "POST", body: JSON.stringify(data) }),
  updateTodo: (id: string, data: object) => request<Todo>(`/todos/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTodo: (id: string) => request<void>(`/todos/${id}`, { method: "DELETE" }),
  completeTodo: (id: string) => request<Todo>(`/todos/${id}/complete`, { method: "POST" }),
  missTodo: (id: string, reason: string) => request<Todo>(`/todos/${id}/miss`, { method: "POST", body: JSON.stringify({ reason }) }),
  notes: (search?: string) => request<Note[]>(search ? `/notes?search=${encodeURIComponent(search)}` : "/notes"),
  createNote: (data: object) => request<Note>("/notes", { method: "POST", body: JSON.stringify(data) }),
  updateNote: (id: string, data: object) => request<Note>(`/notes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteNote: (id: string) => request<void>(`/notes/${id}`, { method: "DELETE" }),
  history: () => request<Transaction[]>("/points/history"),
};
