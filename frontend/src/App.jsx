import { useEffect, useState } from "react";
import { fetchTasks, fetchTaskStats, updateTask } from "./api";
import TaskItem from "./TaskItem";

const USERS = ["alice", "bob", "carol"];

export default function App() {
  const [user, setUser] = useState("alice");
  const [status, setStatus] = useState("");
  const [tasks, setTasks] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [stats, setStats] = useState({ todo: 0, in_progress: 0, done: 0, overdue: 0 });
  const [error, setError] = useState(null);

  const loadStats = () => {
    fetchTaskStats(user)
      .then((data) => setStats(data))
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    loadStats();
  }, [user]);

  useEffect(() => {
    setError(null);
    fetchTasks(user, status)
      .then((data) => {
        setTasks(data.results || []);
        setTotalCount(data.count ?? (data.results ? data.results.length : 0));
      })
      .catch((err) => setError(err.message));
  }, [user, status]);

  const handleMarkDone = async (task) => {
    try {
      const updated = await updateTask(user, task.id, { status: "done" });
      setTasks((prevTasks) =>
        prevTasks.map((t) => (t.id === task.id ? { ...t, ...updated, status: "done", is_overdue: false } : t))
      );
      loadStats();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container">
      <h1>Task Tracker</h1>
      <div className="controls">
        <label>
          Logged in as{" "}
          <select value={user} onChange={(e) => setUser(e.target.value)}>
            {USERS.map((u) => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </label>
        <label>
          Status{" "}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All</option>
            <option value="todo">To do</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
          </select>
        </label>
      </div>

      <div className="stats-bar">
        <div className="stat-card">
          <div className="stat-value">{stats.todo}</div>
          <div className="stat-label">To do</div>
        </div>
        <div className="stat-card in_progress">
          <div className="stat-value">{stats.in_progress}</div>
          <div className="stat-label">In progress</div>
        </div>
        <div className="stat-card done">
          <div className="stat-value">{stats.done}</div>
          <div className="stat-label">Done</div>
        </div>
        <div className="stat-card overdue">
          <div className="stat-value">{stats.overdue}</div>
          <div className="stat-label">Overdue</div>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      <p className="meta">{totalCount} tasks</p>

      <ul className="tasks">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            currentUser={user}
            onMarkDone={handleMarkDone}
          />
        ))}
      </ul>
    </div>
  );
}
