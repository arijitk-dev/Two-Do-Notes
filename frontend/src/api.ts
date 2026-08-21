import type { Accountability, CalendarMonth, DailyReview, Dashboard, Note, Todo, Transaction, User } from "./types";

const API_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  const token = localStorage.getItem("two-do-token");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new Error("Unable to reach the Two Do Notes API. Start the application with Docker Compose and try again.");
  }
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
  todos: (date?: string) => request<Todo[]>(date ? `/todos?date=${encodeURIComponent(date)}` : "/todos"),
  todoHistory: (search?: string) => request<Todo[]>(search ? `/todos/history?search=${encodeURIComponent(search)}` : "/todos/history"),
  reuseTodo: (id: string) => request<Todo>(`/todos/${id}/reuse`, { method: "POST" }),
  reuseTodos: (todoIds: string[]) => request<Todo[]>("/todos/reuse", { method: "POST", body: JSON.stringify({ todo_ids: todoIds }) }),
  unresolved: (date?: string) => request<Todo[]>(date ? `/todos/unresolved?date=${date}` : "/todos/unresolved"),
  calendar: (year: number, month: number) => request<CalendarMonth>(`/calendar?year=${year}&month=${month}`),
  carryForward: (todoIds: string[]) => request<Todo[]>("/todos/carry-forward", { method: "POST", body: JSON.stringify({ todo_ids: todoIds }) }),
  createTodo: (data: object) => request<Todo>("/todos", { method: "POST", body: JSON.stringify(data) }),
  updateTodo: (id: string, data: object) => request<Todo>(`/todos/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteTodo: (id: string) => request<void>(`/todos/${id}`, { method: "DELETE" }),
  completeTodo: (id: string) => request<Todo>(`/todos/${id}/complete`, { method: "POST" }),
  missTodo: (id: string, reason: string, reasonCode?: string, reasonText?: string) => request<Todo>(`/todos/${id}/miss`, { method: "POST", body: JSON.stringify({ reason, reason_code: reasonCode, reason_text: reasonText }) }),
  notes: (search?: string) => request<Note[]>(search ? `/notes?search=${encodeURIComponent(search)}` : "/notes"),
  createNote: (data: object) => request<Note>("/notes", { method: "POST", body: JSON.stringify(data) }),
  updateNote: (id: string, data: object) => request<Note>(`/notes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteNote: (id: string) => request<void>(`/notes/${id}`, { method: "DELETE" }),
  history: () => request<Transaction[]>("/points/history"),
  accountability: (range: "today" | "7d" | "month" = "7d") => request<Accountability>(`/accountability?range=${range}`),
  review: (date: string) => request<DailyReview>(`/reviews/${date}`),
  createReview: (date: string, data: object) => request<DailyReview>(`/reviews/${date}`, { method: "POST", body: JSON.stringify(data) }),
  updateReview: (date: string, data: object) => request<DailyReview>(`/reviews/${date}`, { method: "PATCH", body: JSON.stringify(data) }),
};
