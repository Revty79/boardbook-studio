"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api, mediaUrl } from "@/lib/api";
import { Character } from "@/lib/types";

export default function CharacterDetailPage() {
  const params = useParams<{ id: string; characterId: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);
  const characterId = useMemo(() => Number(params.characterId), [params.characterId]);

  const [character, setCharacter] = useState<Character | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [personality, setPersonality] = useState("");
  const [lockedTraits, setLockedTraits] = useState("");
  const [note, setNote] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const load = async () => {
    const data = await api.getCharacter(projectId, characterId);
    setCharacter(data);
    setName(data.name);
    setDescription(data.description || "");
    setPersonality(data.personality || "");
    setLockedTraits(data.locked_traits.join(", "));
  };

  useEffect(() => {
    if (Number.isFinite(projectId) && Number.isFinite(characterId)) {
      void load();
    }
  }, [projectId, characterId]);

  const onSave = async (event: FormEvent) => {
    event.preventDefault();
    await api.updateCharacter(projectId, characterId, {
      name,
      description,
      personality,
      locked_traits: lockedTraits
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
    });
    await load();
  };

  const onUpload = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    await api.uploadCharacterReference(projectId, characterId, file, note || undefined);
    setFile(null);
    setNote("");
    await load();
  };

  if (!character) {
    return <p className="label">Loading character...</p>;
  }

  return (
    <div className="space-y-5">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Edit Character</h2>
        <form className="grid gap-3 md:grid-cols-2" onSubmit={onSave}>
          <div>
            <label className="label">Name</label>
            <input className="field" value={name} onChange={(event) => setName(event.target.value)} />
          </div>
          <div>
            <label className="label">Personality</label>
            <input className="field" value={personality} onChange={(event) => setPersonality(event.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="label">Description</label>
            <textarea
              className="field min-h-24"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="label">Locked traits</label>
            <input className="field" value={lockedTraits} onChange={(event) => setLockedTraits(event.target.value)} />
          </div>
          <div className="md:col-span-2">
            <button className="btn btn-primary">Save Character</button>
          </div>
        </form>
      </section>

      <section className="card p-4">
        <h3 className="mb-3 text-lg font-bold">Reference Images</h3>
        <form className="mb-4 grid gap-3 md:grid-cols-3" onSubmit={onUpload}>
          <input type="file" accept="image/*" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <input
            className="field"
            placeholder="Optional note"
            value={note}
            onChange={(event) => setNote(event.target.value)}
          />
          <button className="btn btn-secondary" type="submit">
            Upload Reference
          </button>
        </form>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {character.references.map((reference) => (
            <div key={reference.id} className="rounded-xl border border-[#e5d3b2] bg-white p-2">
              <img src={mediaUrl(reference.image_path)} alt="Character reference" className="h-40 w-full rounded-lg object-cover" />
              <p className="label mt-2">{reference.note || "No note"}</p>
            </div>
          ))}
          {character.references.length === 0 && <p className="label">No references uploaded yet.</p>}
        </div>
      </section>
    </div>
  );
}
