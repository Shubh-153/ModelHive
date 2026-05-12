import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

/**
 * Header Component
 * Contains logo and navigation menu.
 */
const Header = () => (
  <header className="header">
    <div className="container header-content">
      <div className="logo">
        <span role="img" aria-label="todo-check">✅</span>
        <span className="logo-text">TaskMaster</span>
      </div>
      <nav className="nav">
        <ul className="nav-list">
          <li><a href="#tasks" className="nav-link">Tasks</a></li>
          <li><a href="#about" className="nav-link">About</a></li>
        </ul>
      </nav>
    </div>
  </header>
);

/**
 * Footer Component
 * Contains copyright, social media links, and contact form.
 */
const Footer = () => (
  <footer className="footer">
    <div className="container footer-grid">
      <div className="footer-info">
        <h3>TaskMaster</h3>
        <p>Your ultimate productivity companion. Organize your life, one task at a time.</p>
        <div className="social-links">
          <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">Twitter</a>
          <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-link">GitHub</a>
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">LinkedIn</a>
        </div>
        <p className="copyright">© 2026 TaskMaster Inc. All rights reserved.</p>
      </div>
      <div className="footer-contact">
        <h3>Contact Us</h3>
        <form className="contact-form" onSubmit={(e) => e.preventDefault()}>
          <input type="email" placeholder="Email Address" required className="form-input" />
          <textarea placeholder="Your Message" rows="3" required className="form-input"></textarea>
          <button type="submit" className="btn btn-secondary">Send Message</button>
        </form>
      </div>
    </div>
  </footer>
);

/**
 * Add Task Component
 * Allows users to add a new task.
 */
const AddTaskComponent = ({ onAdd }) => {
  const [name, setName] = useState('');
  const [dueDate, setDueDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onAdd({ name, due_date: dueDate || null, is_completed: false });
    setName('');
    setDueDate('');
  };

  return (
    <section className="add-task-section card">
      <h2 className="section-title">Add New Task</h2>
      <form className="add-task-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            placeholder="What needs to be done?"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="form-input"
          />
        </div>
        <div className="form-group">
          <input
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="form-input"
          />
        </div>
        <button type="submit" className="btn btn-primary">Add Task</button>
      </form>
    </section>
  );
};

/**
 * Individual Task Item
 * Handles Complete and Delete logic for a single task.
 */
const TaskItem = ({ task, onComplete, onDelete }) => {
  return (
    <li className={`task-item ${task.is_completed ? 'completed' : ''}`}>
      <div className="task-main">
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={() => onComplete(task.id, !task.is_completed)}
          className="task-checkbox"
          title={task.is_completed ? "Mark as incomplete" : "Mark as complete"}
        />
        <div className="task-content">
          <span className="task-name">{task.name}</span>
          {task.due_date && (
            <span className="task-date">
              📅 {new Date(task.due_date).toLocaleString()}
            </span>
          )}
        </div>
      </div>
      <button 
        className="btn btn-icon btn-danger" 
        onClick={() => onDelete(task.id)}
        aria-label="Delete task"
      >
        🗑️
      </button>
    </li>
  );
};

/**
 * Get Tasks Component
 * Displays a list of all tasks.
 */
const GetTasksComponent = ({ tasks, isLoading, error, onComplete, onDelete }) => {
  if (isLoading) return <div className="status-msg">Loading tasks...</div>;
  if (error) return <div className="status-msg error">Error: {error}</div>;

  return (
    <section id="tasks" className="tasks-section card">
      <h2 className="section-title">Your Tasks</h2>
      {tasks.length === 0 ? (
        <p className="empty-msg">No tasks yet.</p>
      ) : (
        <ul className="task-list">
          {tasks.map(task => (
            <TaskItem 
              key={task.id} 
              task={task} 
              onComplete={onComplete} 
              onDelete={onDelete} 
            />
          ))}
        </ul>
      )}
    </section>
  );
};

/**
 * Main App Component
 */
const App = () => {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // GET /tasks
  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/tasks`);
      if (!response.ok) throw new Error('Could not fetch tasks');
      const data = await response.json();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  // POST /tasks
  const addTask = async (taskData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      if (!response.ok) throw new Error('Failed to create task');
      const newTask = await response.json();
      setTasks(prev => [newTask, ...prev]);
    } catch (err) {
      alert(err.message);
    }
  };

  // PUT /tasks/:id
  const toggleTaskStatus = async (id, isCompleted) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_completed: isCompleted }),
      });
      if (!response.ok) throw new Error('Failed to update task');
      const updatedTask = await response.json();
      setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
    } catch (err) {
      alert(err.message);
    }
  };

  // DELETE /tasks/:id
  const deleteTask = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete task');
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="app">
      <Header />
      <main className="container main-content">
        <AddTaskComponent onAdd={addTask} />
        <GetTasksComponent 
          tasks={tasks} 
          isLoading={isLoading} 
          error={error} 
          onComplete={toggleTaskStatus} 
          onDelete={deleteTask} 
        />
      </main>
      <Footer />
    </div>
  );
};

export default App;
