const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type FetchOptions = RequestInit & { token?: string };

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserResponse = {
  id: string;
  email: string;
  full_name: string;
  timezone: string;
  created_at: string;
  updated_at: string;
};

export type UserRegisterInput = {
  email: string;
  password: string;
  full_name: string;
  timezone: string;
};

export type TaskPriority = "low" | "medium" | "high" | "urgent";
export type TaskStatus = "todo" | "doing" | "done" | "snoozed" | "cancelled";
export type TaskSourceType = "manual" | "ai_chat" | "import";

export type Task = {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  category: string;
  priority: TaskPriority;
  status: TaskStatus;
  due_at: string | null;
  estimated_minutes: number | null;
  reminder_at: string | null;
  source_type: TaskSourceType;
  ai_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type TaskCreateInput = {
  title: string;
  description: string;
  category: string;
  priority: TaskPriority;
  status: TaskStatus;
  due_at: string | null;
  estimated_minutes: number | string | null;
  reminder_at: string | null;
  source_type: TaskSourceType;
  ai_metadata: Record<string, unknown> | null;
};

export type TaskUpdateInput = Partial<TaskCreateInput>;

export type TaskListResponse = {
  items: Task[];
  total: number;
};

export type ChatResponse = {
  reply: string;
  intent: "create_task" | "update_task" | "delete_task" | "list_tasks" | "plan_today" | "daily_summary" | "unknown";
  needs_confirmation: boolean;
  missing_fields: string[];
  parsed_task: {
    title: string | null;
    description: string | null;
    category: string | null;
    priority: TaskPriority | null;
    due_at: string | null;
    reminder_at: string | null;
  } | null;
};

export class APIError extends Error {
  constructor(message: string, public readonly status?: number) {
    super(message);
  }
}

async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json")
    ? await response.json().catch(() => null)
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof payload === "string"
        ? payload
        : payload?.detail ?? payload?.message ?? `Request failed (${response.status})`;
    throw new APIError(detail, response.status);
  }

  return payload as T;
}

export const authApi = {
  login(payload: { email: string; password: string }) {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  register(payload: { email: string; password: string; full_name: string; timezone: string }) {
    return request<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

export const taskApi = {
  list(token: string) {
    return request<TaskListResponse>("/tasks", { method: "GET", token });
  },
  create(token: string, payload: TaskCreateInput) {
    return request<Task>("/tasks", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    });
  },
  update(token: string, taskId: string, payload: TaskUpdateInput) {
    return request<Task>(`/tasks/${taskId}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    });
  },
  remove(token: string, taskId: string) {
    return request<{ message: string }>(`/tasks/${taskId}`, {
      method: "DELETE",
      token,
    });
  },
};

export const chatApi = {
  send(token: string, payload: { message: string; conversation_id?: string }) {
    return request<ChatResponse>("/chat", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    });
  },
};
