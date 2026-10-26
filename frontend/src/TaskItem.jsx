export default function TaskItem({ task, currentUser, onMarkDone }) {
  const canEdit =
    currentUser &&
    (task.assigned_to_name === currentUser || task.created_by_name === currentUser);

  return (
    <li className="task">
      <div>
        <strong>{task.title}</strong>
        <div className="meta">
          {task.assigned_to_name} (created by {task.created_by_name}) · due{" "}
          {task.due_date ? new Date(task.due_date).toLocaleString() : "—"}
        </div>
      </div>
      <div className="right">
        {task.is_overdue && <span className="badge overdue">Overdue</span>}
        <span className={`badge ${task.status}`}>{task.status.replace("_", " ")}</span>
        {task.status !== "done" && canEdit && (
          <button onClick={() => onMarkDone(task)}>Mark done</button>
        )}
      </div>
    </li>
  );
}
