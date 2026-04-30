"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { api } from "@/lib/api";
import { Project } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = async () => {
    const data = await api.listProjects();
    setProjects(data);
  };

  useEffect(() => {
    void loadProjects();
  }, []);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await api.createProject({ title, description });
      setTitle("");
      setDescription("");
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create project");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid gap-5 lg:grid-cols-[360px,1fr]">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Create New Project</h2>
        <form className="space-y-3" onSubmit={onSubmit}>
          <div>
            <label className="label">Project title</label>
            <input className="field" value={title} onChange={(event) => setTitle(event.target.value)} required />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea
              className="field min-h-28"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-700">{error}</p>}
          <button className="btn btn-primary w-full" disabled={saving}>
            {saving ? "Creating..." : "Create Project"}
          </button>
        </form>
      </section>

      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Projects</h2>
        <div className="space-y-3">
          {projects.map((project) => (
            <Link
              href={`/projects/${project.id}`}
              key={project.id}
              className="block rounded-xl border border-[#e5d3b2] bg-white/70 p-3 transition hover:bg-white"
            >
              <h3 className="font-bold">{project.title}</h3>
              <p className="label">{project.description || "No description"}</p>
            </Link>
          ))}
          {projects.length === 0 && <p className="label">No projects created yet.</p>}
        </div>
      </section>
    </div>
  );
}
