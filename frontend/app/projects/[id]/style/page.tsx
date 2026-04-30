"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api } from "@/lib/api";
import { StyleProfile } from "@/lib/types";

export default function StyleProfilePage() {
  const params = useParams<{ id: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);

  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [form, setForm] = useState({
    visual_style: "",
    color_palette: "",
    lighting: "",
    composition: "",
    negative_prompt_rules: ""
  });

  const load = async () => {
    const data = await api.getStyleProfile(projectId);
    setProfile(data);
    setForm({
      visual_style: data.visual_style,
      color_palette: data.color_palette,
      lighting: data.lighting,
      composition: data.composition,
      negative_prompt_rules: data.negative_prompt_rules
    });
  };

  useEffect(() => {
    if (Number.isFinite(projectId)) {
      void load();
    }
  }, [projectId]);

  const onSave = async (event: FormEvent) => {
    event.preventDefault();
    await api.upsertStyleProfile(projectId, form);
    await load();
  };

  return (
    <section className="card p-5">
      <h2 className="mb-1 text-xl font-bold">Style Profile</h2>
      <p className="label mb-4">Set a consistent visual direction for this book.</p>
      <form className="space-y-3" onSubmit={onSave}>
        <div>
          <label className="label">Visual style</label>
          <input
            className="field"
            value={form.visual_style}
            onChange={(event) => setForm((prev) => ({ ...prev, visual_style: event.target.value }))}
          />
        </div>
        <div>
          <label className="label">Color palette</label>
          <input
            className="field"
            value={form.color_palette}
            onChange={(event) => setForm((prev) => ({ ...prev, color_palette: event.target.value }))}
          />
        </div>
        <div>
          <label className="label">Lighting</label>
          <input
            className="field"
            value={form.lighting}
            onChange={(event) => setForm((prev) => ({ ...prev, lighting: event.target.value }))}
          />
        </div>
        <div>
          <label className="label">Composition guidance</label>
          <textarea
            className="field min-h-20"
            value={form.composition}
            onChange={(event) => setForm((prev) => ({ ...prev, composition: event.target.value }))}
          />
        </div>
        <div>
          <label className="label">Negative prompt rules</label>
          <textarea
            className="field min-h-20"
            value={form.negative_prompt_rules}
            onChange={(event) => setForm((prev) => ({ ...prev, negative_prompt_rules: event.target.value }))}
          />
        </div>
        <button className="btn btn-primary">Save Style Profile</button>
      </form>
      {profile && <p className="mt-3 text-xs text-[#6f5e4d]">Last updated: {new Date(profile.updated_at).toLocaleString()}</p>}
    </section>
  );
}
