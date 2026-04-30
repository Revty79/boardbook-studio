"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api } from "@/lib/api";
import { ProjectDetail } from "@/lib/types";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const load = async () => {
    const data = await api.getProject(projectId);
    setProject(data);
    setTitle(data.title);
    setDescription(data.description || "");
  };

  useEffect(() => {
    if (Number.isFinite(projectId)) {
      void load();
    }
  }, [projectId]);

  const onSave = async (event: FormEvent) => {
    event.preventDefault();
    await api.updateProject(projectId, { title, description });
    await load();
  };

  if (!project) {
    return <p className="label">Loading project...</p>;
  }

  return (
    <div className="space-y-5">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Project Details</h2>
        <form className="grid gap-3 md:grid-cols-2" onSubmit={onSave}>
          <div>
            <label className="label">Title</label>
            <input className="field" value={title} onChange={(event) => setTitle(event.target.value)} />
          </div>
          <div>
            <label className="label">Description</label>
            <input className="field" value={description} onChange={(event) => setDescription(event.target.value)} />
          </div>
          <div className="md:col-span-2">
            <button className="btn btn-primary">Save Project</button>
          </div>
        </form>
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        <article className="card p-4">
          <p className="label">Characters</p>
          <p className="text-2xl font-bold">{project.stats.character_count}</p>
        </article>
        <article className="card p-4">
          <p className="label">Pages</p>
          <p className="text-2xl font-bold">{project.stats.page_count}</p>
        </article>
        <article className="card p-4">
          <p className="label">Generations</p>
          <p className="text-2xl font-bold">{project.stats.generation_count}</p>
        </article>
      </section>

      <section className="grid gap-3 md:grid-cols-3">
        <Link href={`/projects/${projectId}/characters`} className="card p-4 hover:bg-white/90">
          <h3 className="font-bold">Character Library</h3>
          <p className="label">Create reusable character profiles and references.</p>
        </Link>
        <Link href={`/projects/${projectId}/style`} className="card p-4 hover:bg-white/90">
          <h3 className="font-bold">Style Profile</h3>
          <p className="label">Define visual direction and negative rules.</p>
        </Link>
        <Link href={`/projects/${projectId}/pages`} className="card p-4 hover:bg-white/90">
          <h3 className="font-bold">Story Pages</h3>
          <p className="label">Edit story text, generate images, and refine versions.</p>
        </Link>
      </section>
    </div>
  );
}
