"use client";

import { useEffect, useMemo, useState } from "react";

import {
  APIError,
  authApi,
  chatApi,
  taskApi,
  type ChatResponse,
  type Task,
  type TaskCreateInput,
  type TokenResponse,
  type UserRegisterInput,
  type UserResponse,
} from "@/lib/api";

type AuthMode = "login" | "register";

const emptyTask: TaskCreateInput = {
  title: "",
  description: "",
  category: "general",
  priority: "medium",
  status: "todo",
  due_at: "",
  estimated_minutes: "",
  reminder_at: "",
  source_type: "manual",
  ai_metadata: null,
};

const priorityLabel: Record<Task["priority"], string> = {
  low: "Thấp",
  medium: "Trung bình",
  high: "Cao",
  urgent: "Khẩn",
};

const statusLabel: Record<Task["status"], string> = {
  todo: "Chưa làm",
  doing: "Đang làm",
  done: "Hoàn thành",
  snoozed: "Hoãn",
  cancelled: "Đã hủy",
};

const inputClass =
  "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:ring-2 focus:ring-sky-200";
const inputClassDark =
  "w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400 focus:ring-2 focus:ring-sky-500/30";

export default function Home() {
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [authForm, setAuthForm] = useState<UserRegisterInput>({
    email: "",
    password: "",
    full_name: "",
    timezone: "Asia/Ho_Chi_Minh",
  });
  const [authBusy, setAuthBusy] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [taskForm, setTaskForm] = useState<TaskCreateInput>(emptyTask);
  const [taskBusy, setTaskBusy] = useState(false);
  const [taskError, setTaskError] = useState<string | null>(null);

  const [chatMessage, setChatMessage] = useState("");
  const [chatReplies, setChatReplies] = useState<ChatResponse[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = window.localStorage.getItem("ai-task-token");
    const savedUser = window.localStorage.getItem("ai-task-user");
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser) as UserResponse);
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    void loadTasks(token);
  }, [token]);

  const selectedTask = useMemo(
    () => tasks.find((task) => task.id === selectedTaskId) ?? null,
    [selectedTaskId, tasks],
  );

  const totalTasks = tasks.length;
  const doneTasks = tasks.filter((task) => task.status === "done").length;
  const urgentTasks = tasks.filter((task) => task.priority === "urgent").length;

  async function loadTasks(currentToken: string) {
    try {
      const response = await taskApi.list(currentToken);
      setTasks(response.items);
      setSelectedTaskId((current) => current ?? response.items[0]?.id ?? null);
    } catch (error) {
      setTaskError(error instanceof Error ? error.message : "Không tải được task");
    }
  }

  async function handleAuth() {
    setAuthError(null);
    setAuthBusy(true);

    try {
      let profile: UserResponse;

      if (authMode === "register") {
        profile = await authApi.register(authForm);
      } else {
        const tokenResponse: TokenResponse = await authApi.login({
          email: authForm.email,
          password: authForm.password,
        });
        profile = {
          id: "local",
          email: authForm.email,
          full_name: authForm.full_name || authForm.email,
          timezone: authForm.timezone,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        window.localStorage.setItem("ai-task-token", tokenResponse.access_token);
        window.localStorage.setItem("ai-task-user", JSON.stringify(profile));
        setToken(tokenResponse.access_token);
        setUser(profile);
        await loadTasks(tokenResponse.access_token);
        return;
      }

      const tokenResponse: TokenResponse = await authApi.login({
        email: authForm.email,
        password: authForm.password,
      });

      window.localStorage.setItem("ai-task-token", tokenResponse.access_token);
      window.localStorage.setItem("ai-task-user", JSON.stringify(profile));
      setToken(tokenResponse.access_token);
      setUser(profile);
      await loadTasks(tokenResponse.access_token);
    } catch (error) {
      setAuthError(error instanceof APIError ? error.message : "Đăng nhập thất bại");
    } finally {
      setAuthBusy(false);
    }
  }

  async function handleCreateTask() {
    if (!token) return;
    setTaskError(null);
    setTaskBusy(true);

    try {
      await taskApi.create(token, {
        ...taskForm,
        due_at: taskForm.due_at || null,
        reminder_at: taskForm.reminder_at || null,
        estimated_minutes: taskForm.estimated_minutes
          ? Number(taskForm.estimated_minutes)
          : null,
      });
      setTaskForm(emptyTask);
      await loadTasks(token);
    } catch (error) {
      setTaskError(error instanceof Error ? error.message : "Không tạo được task");
    } finally {
      setTaskBusy(false);
    }
  }

  async function handleTaskPatch(taskId: string, status: Task["status"]) {
    if (!token) return;
    setTaskBusy(true);
    try {
      await taskApi.update(token, taskId, { status });
      await loadTasks(token);
    } finally {
      setTaskBusy(false);
    }
  }

  async function handleDeleteTask(taskId: string) {
    if (!token) return;
    setTaskBusy(true);
    try {
      await taskApi.remove(token, taskId);
      await loadTasks(token);
    } finally {
      setTaskBusy(false);
    }
  }

  async function handleChat() {
    if (!token || !chatMessage.trim()) return;
    setChatError(null);
    setChatBusy(true);
    try {
      const response = await chatApi.send(token, {
        message: chatMessage,
        conversation_id: "main",
      });
      setChatReplies((current) => [response, ...current]);
      setChatMessage("");
      await loadTasks(token);
    } catch (error) {
      setChatError(error instanceof Error ? error.message : "Chat thất bại");
    } finally {
      setChatBusy(false);
    }
  }

  function handleLogout() {
    window.localStorage.removeItem("ai-task-token");
    window.localStorage.removeItem("ai-task-user");
    setToken(null);
    setUser(null);
    setTasks([]);
    setSelectedTaskId(null);
    setChatReplies([]);
  }

  if (!token || !user) {
    return (
      <main className="min-h-screen bg-[radial-gradient(circle_at_top,#1d4ed8_0%,#0f172a_42%,#020617_100%)] px-4 py-10 text-slate-100 sm:px-6 lg:px-8">
        <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <section className="space-y-6">
            <span className="inline-flex items-center rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-sky-200 backdrop-blur">
              AI Task Manager · React Frontend
            </span>
            <div className="space-y-4">
              <h1 className="max-w-2xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Quản lý công việc cá nhân bằng dashboard, task list và AI chat.
              </h1>
              <p className="max-w-xl text-base leading-7 text-slate-300 sm:text-lg">
                Đăng nhập để tạo task, chat với AI, theo dõi tiến độ và xem tổng quan trong một giao diện React hiện đại.
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <StatCard label="Task hôm nay" value={`${totalTasks}`} />
              <StatCard label="Hoàn thành" value={`${doneTasks}`} />
              <StatCard label="Ưu tiên cao" value={`${urgentTasks}`} />
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/95 p-6 text-slate-900 shadow-2xl shadow-slate-950/30 backdrop-blur">
            <div className="mb-6 flex rounded-2xl bg-slate-100 p-1">
              <button
                className={`flex-1 rounded-xl px-4 py-2 text-sm font-medium transition ${
                  authMode === "login" ? "bg-white text-slate-900 shadow" : "text-slate-500"
                }`}
                onClick={() => setAuthMode("login")}
                type="button"
              >
                Đăng nhập
              </button>
              <button
                className={`flex-1 rounded-xl px-4 py-2 text-sm font-medium transition ${
                  authMode === "register" ? "bg-white text-slate-900 shadow" : "text-slate-500"
                }`}
                onClick={() => setAuthMode("register")}
                type="button"
              >
                Đăng ký
              </button>
            </div>

            <div className="space-y-4">
              {authMode === "register" && (
                <Field label="Họ tên">
                  <input
                    className={inputClass}
                    value={authForm.full_name}
                    onChange={(event) =>
                      setAuthForm((current) => ({ ...current, full_name: event.target.value }))
                    }
                    placeholder="Nguyễn Văn A"
                  />
                </Field>
              )}
              <Field label="Email">
                <input
                  className={inputClass}
                  value={authForm.email}
                  onChange={(event) =>
                    setAuthForm((current) => ({ ...current, email: event.target.value }))
                  }
                  type="email"
                  placeholder="you@example.com"
                />
              </Field>
              <Field label="Mật khẩu">
                <input
                  className={inputClass}
                  value={authForm.password}
                  onChange={(event) =>
                    setAuthForm((current) => ({ ...current, password: event.target.value }))
                  }
                  type="password"
                  placeholder="••••••••"
                />
              </Field>
              {authMode === "register" && (
                <Field label="Timezone">
                  <input
                    className={inputClass}
                    value={authForm.timezone}
                    onChange={(event) =>
                      setAuthForm((current) => ({ ...current, timezone: event.target.value }))
                    }
                    placeholder="Asia/Ho_Chi_Minh"
                  />
                </Field>
              )}

              {authError && <Notice tone="error" text={authError} />}

              <button
                className="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={authBusy}
                onClick={() => void handleAuth()}
                type="button"
              >
                {authBusy ? "Đang xử lý..." : authMode === "login" ? "Đăng nhập" : "Đăng ký & đăng nhập"}
              </button>
            </div>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-black/20 backdrop-blur lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-sky-300">Personal AI Task Manager</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Xin chào, {user.full_name}</h2>
            <p className="text-sm text-slate-400">
              {user.email} · {user.timezone}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <StatMini label="Tổng task" value={totalTasks} />
            <StatMini label="Done" value={doneTasks} />
            <StatMini label="High+Urgent" value={urgentTasks} />
            <button
              className="rounded-2xl border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10"
              onClick={handleLogout}
              type="button"
            >
              Đăng xuất
            </button>
          </div>
        </header>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <Panel title="Thêm task nhanh">
              <div className="grid gap-4 md:grid-cols-2">
                <Field label="Tiêu đề">
                  <input
                    className={inputClassDark}
                    value={taskForm.title}
                    onChange={(event) =>
                      setTaskForm((current) => ({ ...current, title: event.target.value }))
                    }
                    placeholder="Chuẩn bị slide họp"
                  />
                </Field>
                <Field label="Category">
                  <input
                    className={inputClassDark}
                    value={taskForm.category}
                    onChange={(event) =>
                      setTaskForm((current) => ({ ...current, category: event.target.value }))
                    }
                    placeholder="work"
                  />
                </Field>
                <Field label="Priority">
                  <select
                    className={inputClassDark}
                    value={taskForm.priority}
                    onChange={(event) =>
                      setTaskForm((current) => ({
                        ...current,
                        priority: event.target.value as Task["priority"],
                      }))
                    }
                  >
                    {Object.entries(priorityLabel).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Status">
                  <select
                    className={inputClassDark}
                    value={taskForm.status}
                    onChange={(event) =>
                      setTaskForm((current) => ({
                        ...current,
                        status: event.target.value as Task["status"],
                      }))
                    }
                  >
                    {Object.entries(statusLabel).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Due at">
                  <input
                    className={inputClassDark}
                    value={taskForm.due_at}
                    onChange={(event) =>
                      setTaskForm((current) => ({ ...current, due_at: event.target.value }))
                    }
                    type="datetime-local"
                  />
                </Field>
                <Field label="Reminder at">
                  <input
                    className={inputClassDark}
                    value={taskForm.reminder_at}
                    onChange={(event) =>
                      setTaskForm((current) => ({ ...current, reminder_at: event.target.value }))
                    }
                    type="datetime-local"
                  />
                </Field>
                <Field label="Estimated minutes">
                  <input
                    className={inputClassDark}
                    value={taskForm.estimated_minutes}
                    onChange={(event) =>
                      setTaskForm((current) => ({ ...current, estimated_minutes: event.target.value }))
                    }
                    type="number"
                    min={1}
                    placeholder="60"
                  />
                </Field>
              </div>

              <Field label="Mô tả">
                <textarea
                  className={`${inputClassDark} min-h-28`}
                  value={taskForm.description}
                  onChange={(event) =>
                    setTaskForm((current) => ({ ...current, description: event.target.value }))
                  }
                  placeholder="Chi tiết task..."
                />
              </Field>

              <div className="flex flex-wrap gap-3">
                <button
                  className="rounded-2xl bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={taskBusy || !taskForm.title.trim()}
                  onClick={() => void handleCreateTask()}
                  type="button"
                >
                  {taskBusy ? "Đang lưu..." : "Tạo task"}
                </button>
                <button
                  className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
                  onClick={() => setTaskForm(emptyTask)}
                  type="button"
                >
                  Reset form
                </button>
              </div>

              {taskError && <Notice tone="error" text={taskError} />}
            </Panel>

            <Panel title="Danh sách task">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {tasks.map((task) => (
                  <article
                    key={task.id}
                    className={`rounded-3xl border p-4 transition ${
                      task.id === selectedTaskId
                        ? "border-sky-400/60 bg-sky-500/10"
                        : "border-white/10 bg-white/5 hover:bg-white/10"
                    }`}
                    onClick={() => setSelectedTaskId(task.id)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-semibold text-white">{task.title}</h3>
                        <p className="mt-1 text-sm text-slate-400">{task.category}</p>
                      </div>
                      <span className={badgeClass(task.priority)}>{priorityLabel[task.priority]}</span>
                    </div>

                    <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-300">
                      {task.description || "Chưa có mô tả"}
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
                      <Chip text={statusLabel[task.status]} />
                      <Chip text={`Due: ${formatDateTime(task.due_at)}`} />
                    </div>

                    <div className="mt-4 flex gap-2">
                      <button
                        className="rounded-xl bg-emerald-500/20 px-3 py-2 text-xs font-semibold text-emerald-200 transition hover:bg-emerald-500/30"
                        onClick={(event) => {
                          event.stopPropagation();
                          void handleTaskPatch(task.id, "done");
                        }}
                        type="button"
                      >
                        Done
                      </button>
                      <button
                        className="rounded-xl bg-amber-500/20 px-3 py-2 text-xs font-semibold text-amber-200 transition hover:bg-amber-500/30"
                        onClick={(event) => {
                          event.stopPropagation();
                          void handleTaskPatch(task.id, "doing");
                        }}
                        type="button"
                      >
                        Doing
                      </button>
                      <button
                        className="rounded-xl bg-rose-500/20 px-3 py-2 text-xs font-semibold text-rose-200 transition hover:bg-rose-500/30"
                        onClick={(event) => {
                          event.stopPropagation();
                          void handleDeleteTask(task.id);
                        }}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </Panel>
          </div>

          <div className="space-y-6">
            <Panel title="AI chat">
              <div className="space-y-3">
                <textarea
                  className={`${inputClassDark} min-h-32`}
                  value={chatMessage}
                  onChange={(event) => setChatMessage(event.target.value)}
                  placeholder='Ví dụ: "Ngày mai 9h nhắc tôi họp và tạo task chuẩn bị slide"'
                />
                <button
                  className="w-full rounded-2xl bg-gradient-to-r from-sky-500 to-indigo-500 px-4 py-3 text-sm font-semibold text-white transition hover:from-sky-400 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={chatBusy || !chatMessage.trim()}
                  onClick={() => void handleChat()}
                  type="button"
                >
                  {chatBusy ? "Đang xử lý..." : "Gửi cho AI"}
                </button>
                {chatError && <Notice tone="error" text={chatError} />}
              </div>

              <div className="mt-6 space-y-3">
                {chatReplies.length === 0 ? (
                  <p className="text-sm text-slate-400">
                    AI reply sẽ hiển thị ở đây sau khi gửi tin nhắn.
                  </p>
                ) : (
                  chatReplies.map((reply, index) => (
                    <div key={`${reply.intent}-${index}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-xs uppercase tracking-[0.3em] text-sky-300">
                          {reply.intent}
                        </span>
                        {reply.needs_confirmation && (
                          <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs text-amber-200">
                            Cần xác nhận
                          </span>
                        )}
                      </div>
                      <p className="mt-3 text-sm leading-6 text-slate-200">{reply.reply}</p>
                      {reply.parsed_task && (
                        <pre className="mt-4 overflow-auto rounded-2xl bg-slate-950/60 p-3 text-xs text-slate-300">
                          {JSON.stringify(reply.parsed_task, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))
                )}
              </div>
            </Panel>

            <Panel title="Task detail">
              {selectedTask ? (
                <div className="space-y-4 text-sm text-slate-300">
                  <div>
                    <h3 className="text-xl font-semibold text-white">{selectedTask.title}</h3>
                    <p className="mt-1 text-slate-400">{selectedTask.category}</p>
                  </div>
                  <InfoRow label="Priority" value={priorityLabel[selectedTask.priority]} />
                  <InfoRow label="Status" value={statusLabel[selectedTask.status]} />
                  <InfoRow label="Due at" value={formatDateTime(selectedTask.due_at)} />
                  <InfoRow label="Reminder" value={formatDateTime(selectedTask.reminder_at)} />
                  <InfoRow
                    label="Estimated"
                    value={selectedTask.estimated_minutes ? `${selectedTask.estimated_minutes} phút` : "Chưa có"}
                  />
                  <InfoRow label="Source" value={selectedTask.source_type} />
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-slate-300">
                    {selectedTask.description || "Chưa có mô tả"}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-400">Chưa chọn task nào.</p>
              )}
            </Panel>

            <Panel title="Tổng quan nhanh">
              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <QuickStat label="Task đã tạo" value={totalTasks} />
                <QuickStat label="Task hoàn thành" value={doneTasks} />
                <QuickStat label="Task ưu tiên cao" value={urgentTasks} />
              </div>
            </Panel>
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur">
      <div className="text-sm text-slate-300">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
    </div>
  );
}

function StatMini({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-center">
      <div className="text-[11px] uppercase tracking-[0.25em] text-slate-400">{label}</div>
      <div className="mt-1 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl shadow-black/10 backdrop-blur">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-2 text-sm text-slate-300">
      <span className="font-medium text-slate-200">{label}</span>
      {children}
    </label>
  );
}

function Notice({ tone, text }: { tone: "error" | "info"; text: string }) {
  const cls =
    tone === "error"
      ? "border-rose-500/30 bg-rose-500/10 text-rose-100"
      : "border-sky-500/30 bg-sky-500/10 text-sky-100";
  return <div className={`rounded-2xl border px-4 py-3 text-sm ${cls}`}>{text}</div>;
}

function Chip({ text }: { text: string }) {
  return <span className="rounded-full bg-white/10 px-3 py-1">{text}</span>;
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <span className="text-slate-400">{label}</span>
      <span className="font-medium text-white">{value}</span>
    </div>
  );
}

function QuickStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-4">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
    </div>
  );
}

function badgeClass(priority: Task["priority"]) {
  switch (priority) {
    case "urgent":
      return "rounded-full bg-rose-500/20 px-3 py-1 text-xs font-semibold text-rose-200";
    case "high":
      return "rounded-full bg-amber-500/20 px-3 py-1 text-xs font-semibold text-amber-200";
    case "low":
      return "rounded-full bg-slate-500/20 px-3 py-1 text-xs font-semibold text-slate-200";
    default:
      return "rounded-full bg-sky-500/20 px-3 py-1 text-xs font-semibold text-sky-200";
  }
}

function formatDateTime(value: string | null) {
  if (!value) return "Chưa có";
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
