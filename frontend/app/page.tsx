"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { DashboardSummary, Project } from "@/lib/types";

const emptySummary: DashboardSummary = {
  project_count: 0,
  character_count: 0,
  page_count: 0,
  generation_count: 0
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    void Promise.all([api.getDashboardSummary(), api.listProjects()]).then(([s, p]) => {
      setSummary(s);
      setProjects(p.slice(0, 3));
    });
  }, []);

  return (
    <div className="space-y-5">
      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <article className="card p-4">
          <p className="label">Projects</p>
          <p className="text-3xl font-bold">{summary.project_count}</p>
        </article>
        <article className="card p-4">
          <p className="label">Characters</p>
          <p className="text-3xl font-bold">{summary.character_count}</p>
        </article>
        <article className="card p-4">
          <p className="label">Story Pages</p>
          <p className="text-3xl font-bold">{summary.page_count}</p>
        </article>
        <article className="card p-4">
          <p className="label">Generations</p>
          <p className="text-3xl font-bold">{summary.generation_count}</p>
        </article>
      </section>

      <section className="card p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Recent Projects</h2>
            <p className="label">Pick a project to continue illustrating.</p>
          </div>
          <Link href="/projects" className="btn btn-primary">
            Open Projects
          </Link>
        </div>

        {projects.length === 0 ? (
          <p className="label">No projects yet. Create one from the Projects page.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-3">
            {projects.map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`} className="card p-4 transition hover:-translate-y-0.5">
                <h3 className="text-lg font-bold">{project.title}</h3>
                <p className="label mt-1 line-clamp-3">{project.description || "No description yet."}</p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
