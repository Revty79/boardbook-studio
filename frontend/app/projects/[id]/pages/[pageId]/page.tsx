"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api, mediaUrl } from "@/lib/api";
import { Generation, StoryPage } from "@/lib/types";

export default function PageEditorPage() {
  const params = useParams<{ id: string; pageId: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);
  const pageId = useMemo(() => Number(params.pageId), [params.pageId]);

  const [page, setPage] = useState<StoryPage | null>(null);
  const [title, setTitle] = useState("");
  const [pageNumber, setPageNumber] = useState(1);
  const [textContent, setTextContent] = useState("");

  const [generations, setGenerations] = useState<Generation[]>([]);
  const [selectedGenerationId, setSelectedGenerationId] = useState<number | null>(null);

  const [refinement, setRefinement] = useState("");
  const [promptPreview, setPromptPreview] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedGeneration = generations.find((generation) => generation.id === selectedGenerationId) || null;

  const loadAll = async () => {
    const [pageData, generationData] = await Promise.all([api.getPage(projectId, pageId), api.listPageGenerations(pageId)]);
    setPage(pageData);
    setTitle(pageData.title);
    setPageNumber(pageData.page_number);
    setTextContent(pageData.text_content);

    setGenerations(generationData);
    if (generationData.length > 0) {
      const approved = generationData.find((item) => item.id === pageData.approved_generation_id);
      setSelectedGenerationId((approved || generationData[0]).id);
    } else {
      setSelectedGenerationId(null);
    }
  };

  useEffect(() => {
    if (Number.isFinite(projectId) && Number.isFinite(pageId)) {
      void loadAll();
    }
  }, [projectId, pageId]);

  const savePage = async (event: FormEvent) => {
    event.preventDefault();
    setWorking(true);
    try {
      await api.updatePage(projectId, pageId, { title, page_number: pageNumber, text_content: textContent });
      await loadAll();
    } finally {
      setWorking(false);
    }
  };

  const generate = async () => {
    setWorking(true);
    setError(null);
    try {
      await api.updatePage(projectId, pageId, { title, page_number: pageNumber, text_content: textContent });
      await api.generateImage(pageId);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setWorking(false);
    }
  };

  const previewPrompt = async () => {
    setWorking(true);
    setError(null);
    try {
      await api.updatePage(projectId, pageId, { title, page_number: pageNumber, text_content: textContent });
      const prompt = await api.buildPrompt(pageId);
      setPromptPreview(`${prompt.prompt}\n\nNegative prompt:\n${prompt.negative_prompt}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prompt build failed");
    } finally {
      setWorking(false);
    }
  };

  const refine = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedGenerationId || !refinement.trim()) {
      return;
    }

    setWorking(true);
    setError(null);
    try {
      const next = await api.refineGeneration(pageId, selectedGenerationId, refinement.trim());
      setRefinement("");
      await loadAll();
      setSelectedGenerationId(next.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Refinement failed");
    } finally {
      setWorking(false);
    }
  };

  const approve = async () => {
    if (!selectedGenerationId) return;
    setWorking(true);
    setError(null);
    try {
      await api.approveGeneration(selectedGenerationId);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approval failed");
    } finally {
      setWorking(false);
    }
  };

  if (!page) {
    return <p className="label">Loading page editor...</p>;
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1.1fr,0.9fr]">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Story Page Controls</h2>
        <form className="space-y-3" onSubmit={savePage}>
          <div className="grid gap-3 md:grid-cols-2">
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
          </div>
          <div>
            <label className="label">Story text</label>
            <textarea className="field min-h-64" value={textContent} onChange={(event) => setTextContent(event.target.value)} />
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="btn btn-outline" type="submit" disabled={working}>
              Save Text
            </button>
            <button className="btn btn-secondary" type="button" onClick={previewPrompt} disabled={working}>
              Preview Prompt
            </button>
            <button className="btn btn-primary" type="button" onClick={generate} disabled={working}>
              Generate Image
            </button>
          </div>
          {promptPreview && (
            <pre className="max-h-64 overflow-auto rounded-xl border border-[#dcc9a8] bg-[#fffaf0] p-3 text-xs whitespace-pre-wrap">
              {promptPreview}
            </pre>
          )}
        </form>
      </section>

      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Preview and Versions</h2>
        <div className="space-y-3">
          <div className="overflow-hidden rounded-xl border border-[#e1cead] bg-white">
            {selectedGeneration ? (
              <img src={mediaUrl(selectedGeneration.image_path)} alt="Generated illustration" className="h-72 w-full object-cover" />
            ) : (
              <div className="flex h-72 items-center justify-center text-sm text-[#806d57]">No generation yet.</div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <p className="label">
              {selectedGeneration
                ? `Selected generation #${selectedGeneration.id} (${selectedGeneration.generation_type})`
                : "Create your first generation"}
            </p>
            <button className="btn btn-primary" onClick={approve} disabled={!selectedGeneration || working}>
              Approve Selected
            </button>
          </div>

          <div className="max-h-52 space-y-2 overflow-auto rounded-xl border border-[#e1cead] bg-white/70 p-2">
            {generations.map((generation) => {
              const isSelected = generation.id === selectedGenerationId;
              return (
                <button
                  key={generation.id}
                  className={`w-full rounded-lg border p-2 text-left ${
                    isSelected ? "border-[#8ec3a8] bg-[#eaf6ef]" : "border-[#e6d6b8] bg-white"
                  }`}
                  onClick={() => setSelectedGenerationId(generation.id)}
                >
                  <p className="text-sm font-bold">#{generation.id} - {generation.generation_type}</p>
                  <p className="text-xs text-[#6c5a49]">{new Date(generation.created_at).toLocaleString()}</p>
                  {page.approved_generation_id === generation.id && (
                    <p className="mt-1 text-xs font-bold text-[#1c5a35]">Approved for page</p>
                  )}
                </button>
              );
            })}
            {generations.length === 0 && <p className="label">No versions yet.</p>}
          </div>

          <form className="space-y-2 rounded-xl border border-[#e1cead] bg-[#fffaf2] p-3" onSubmit={refine}>
            <p className="text-sm font-bold">Refine this illustration</p>
            <textarea
              className="field min-h-20"
              placeholder="Example: keep the character the same but change pajamas to blue"
              value={refinement}
              onChange={(event) => setRefinement(event.target.value)}
            />
            <button className="btn btn-secondary w-full" disabled={!selectedGeneration || working}>
              Send Refinement
            </button>
          </form>

          {error && <p className="text-sm text-red-700">{error}</p>}
        </div>
      </section>
    </div>
  );
}
