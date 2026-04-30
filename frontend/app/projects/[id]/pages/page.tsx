"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api } from "@/lib/api";
import { StoryPage } from "@/lib/types";

export default function StoryPagesPage() {
  const params = useParams<{ id: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);

  const [pages, setPages] = useState<StoryPage[]>([]);
  const [title, setTitle] = useState("Page 1");
  const [pageNumber, setPageNumber] = useState(1);
  const [textContent, setTextContent] = useState("");

  const load = async () => {
    const data = await api.listPages(projectId);
    setPages(data);
  };

  useEffect(() => {
    if (Number.isFinite(projectId)) {
      void load();
    }
  }, [projectId]);

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    await api.createPage(projectId, {
      title,
      page_number: pageNumber,
      text_content: textContent
    });
    setTextContent("");
    await load();
  };

  return (
    <div className="grid gap-5 lg:grid-cols-[360px,1fr]">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Add Story Page</h2>
        <form className="space-y-3" onSubmit={onCreate}>
          <div>
            <label className="label">Page title</label>
            <input className="field" value={title} onChange={(event) => setTitle(event.target.value)} />
          </div>
          <div>
            <label className="label">Page number</label>
            <input
              className="field"
              type="number"
              value={pageNumber}
              onChange={(event) => setPageNumber(Number(event.target.value))}
            />
          </div>
          <div>
            <label className="label">Story text</label>
            <textarea
              className="field min-h-28"
              value={textContent}
              onChange={(event) => setTextContent(event.target.value)}
            />
          </div>
          <button className="btn btn-primary w-full">Create Page</button>
        </form>
      </section>

      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Story Pages</h2>
        <div className="space-y-3">
          {pages.map((page) => (
            <Link
              key={page.id}
              href={`/projects/${projectId}/pages/${page.id}`}
              className="block rounded-xl border border-[#e5d3b2] bg-white/70 p-3"
            >
              <h3 className="font-bold">{page.title}</h3>
              <p className="label">Page {page.page_number}</p>
              <p className="mt-1 text-sm text-[#5b4d3f] line-clamp-2">{page.text_content || "No text yet"}</p>
            </Link>
          ))}
          {pages.length === 0 && <p className="label">No story pages yet.</p>}
        </div>
      </section>
    </div>
  );
}
